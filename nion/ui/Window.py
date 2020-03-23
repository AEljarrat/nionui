"""
A basic class to serve as the document controller of a typical one window application.
"""

# standard libraries
import asyncio
import collections
import functools
import gettext
import logging
import typing

# local libraries
from nion.utils import Event
from nion.utils import Geometry
from nion.utils import Process
from nion.ui import UserInterface


_ = gettext.gettext


ActionContext = collections.namedtuple("ActionContext", ["application", "window", "focus_widget"])


class Action:
    action_id = None
    action_name = None
    action_summary = None
    action_description = None

    def invoke(self, context: ActionContext) -> None: ...

    def is_checked(self, context: ActionContext) -> bool:
        return False

    def is_enabled(self, context: ActionContext) -> bool:
        return True

    def get_action_name(self, context: ActionContext) -> str:
        return self.action_name

actions = dict()

def register_action(action: Action) -> None:
    assert not action.action_id in actions
    actions[action.action_id] = action


action_shortcuts = dict()

def add_action_shortcut(action_id: str, action_context: str, key_sequence: str) -> None:
    action_shortcuts.setdefault(action_id, dict())[action_context] = key_sequence

def register_action_shortcuts(action_shortcuts: typing.Mapping) -> None:
    for action_id, action_shortcut_d in action_shortcuts.items():
        for action_context, key_sequence in action_shortcut_d.items():
            add_action_shortcut(action_id, action_context, key_sequence)

def get_action_id_for_key(context: str, key) -> typing.Optional[str]:
    for action_id, action_shortcut_d in action_shortcuts.items():
        for action_context, key_sequence in action_shortcut_d.items():
            if action_context == context and key.text == key_sequence:  # TODO: match the actual key sequence
                return action_id
    return None


class Window:

    def __init__(self, ui: UserInterface.UserInterface, app=None, parent_window=None, window_style=None, persistent_id=None):
        self.ui = ui
        self.app = app
        self.on_close = None
        parent_window = parent_window._document_window if parent_window else None
        self.__document_window = self.ui.create_document_window(parent_window=parent_window)
        if window_style:
            self.__document_window.window_style = window_style
        self.__persistent_id = persistent_id
        self.__shown = False

        self._window_close_event = Event.Event()

        self.__document_window.on_periodic = self.periodic
        self.__document_window.on_queue_task = self.queue_task
        self.__document_window.on_clear_queued_tasks = self.clear_queued_tasks
        self.__document_window.on_add_task = self.add_task
        self.__document_window.on_clear_task = self.clear_task
        self.__document_window.on_about_to_show = self.about_to_show
        self.__document_window.on_about_to_close = self.about_to_close
        self.__document_window.on_activation_changed = self.activation_changed
        self.__document_window.on_key_pressed = self.key_pressed
        self.__document_window.on_key_released = self.key_released
        self.__document_window.on_size_changed = self.size_changed
        self.__document_window.on_position_changed = self.position_changed
        self.__document_window.on_refocus_widget = self.refocus_widget
        self.__document_window.on_ui_activity = self._register_ui_activity
        self.__periodic_queue = Process.TaskQueue()
        self.__periodic_set = Process.TaskSet()

        # define old-style menu actions for backwards compatibility
        self._close_action = None
        self._page_setup_action = None
        self._print_action = None
        self._quit_action = None
        self._undo_action = None
        self._redo_action = None
        self._cut_action = None
        self._copy_action = None
        self._paste_action = None
        self._delete_action = None
        self._select_all_action = None
        self._minimize_action = None
        self._zoom_action = None
        self._bring_to_front_action = None

        # configure the event loop object
        logger = logging.getLogger()
        old_level = logger.level
        logger.setLevel(logging.INFO)
        self.__event_loop = asyncio.new_event_loop()  # outputs a debugger message!
        logger.setLevel(old_level)

        if app: app._window_created(self)

    def close(self):
        self._window_close_event.fire(self)
        self._window_close_event = None
        self.on_close = None
        Process.close_event_loop(self.__event_loop)
        self.__event_loop = None
        self.ui.destroy_document_window(self.__document_window)  # close the ui window
        self.__document_window = None
        self.__periodic_queue = None
        self.__periodic_set = None
        self._close_action = None
        self._page_setup_action = None
        self._print_action = None
        self._quit_action = None
        self._undo_action = None
        self._redo_action = None
        self._cut_action = None
        self._copy_action = None
        self._paste_action = None
        self._delete_action = None
        self._select_all_action = None
        self._minimize_action = None
        self._zoom_action = None
        self._bring_to_front_action = None
        self.app = None

    @property
    def _document_window(self):
        # for testing only
        return self.__document_window

    def _create_menus(self):
        menu_descriptions = [
            {"type": "menu", "menu_id": "file", "title": _("File"), "items":
                [
                    {"type": "item", "action_id": "window.close"},
                    {"type": "separator"},
                    {"type": "item", "action_id": "window.page_setup"},
                    {"type": "item", "action_id": "window.print"},
                    {"type": "separator"},
                    {"type": "item", "action_id": "application.exit"},
                ]
             },
            {"type": "menu", "menu_id": "edit", "title": _("Edit"), "items":
                [
                    {"type": "item", "action_id": "window.undo"},
                    {"type": "item", "action_id": "window.redo"},
                    {"type": "separator"},
                    {"type": "item", "action_id": "window.cut"},
                    {"type": "item", "action_id": "window.copy"},
                    {"type": "item", "action_id": "window.paste"},
                    {"type": "item", "action_id": "window.delete"},
                    {"type": "item", "action_id": "window.select_all"},
                ]
             },
            {"type": "menu", "menu_id": "window", "title": _("Window"), "items":
                [
                    {"type": "item", "action_id": "window.minimize"},
                    {"type": "separator"},
                    {"type": "item", "action_id": "window.zoom"},
                    {"type": "item", "action_id": "window.bring_to_front"},
                ]
             },
            {"type": "menu", "menu_id": "help", "title": _("Help"), "items":
                [
                ]
             },
        ]

        self.build_menu(None, menu_descriptions)

    def _adjust_menus(self) -> None:
        # called when key may be shortcut. does not work for sub-menus.
        for menu in self.__document_window.menus:
            self._menu_about_to_show(menu)

    def _request_exit(self) -> None:
        if self.app:
            self.app.exit()

    def request_close(self) -> None:
        self.__document_window.request_close()

    def _register_ui_activity(self) -> None:
        pass

    def finish_periodic(self) -> None:
        # recognize when we're running as test and finish out periodic operations
        if not self.__document_window.has_event_loop:
            self.periodic()

    def periodic(self) -> None:
        self.__periodic_queue.perform_tasks()
        self.__periodic_set.perform_tasks()
        self.__event_loop.stop()
        self.__event_loop.run_forever()
        if self.app:
            self.app.periodic()

    @property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        return self.__event_loop

    def attach_widget(self, widget):
        self.__document_window.attach(widget)

    def detach_widget(self):
        self.__document_window.detach()

    def about_to_show(self) -> None:
        if self.__persistent_id:
            geometry = self.ui.get_persistent_string("{}/Geometry".format(self.__persistent_id))
            state = self.ui.get_persistent_string("{}/State".format(self.__persistent_id))
            self.restore(geometry, state)
        self.__shown = True

    def about_to_close(self, geometry: str, state: str) -> None:
        # this method is invoked when the low level window is about to close.
        # subclasses can override this method to save geometry and state.
        if callable(self.on_close):
            self.on_close()
        # this call will close this object and subsequently the ui window, but not the low level window itself.
        # it will, however, delete the widget hierarchy as a consequence of closing the ui window.
        # so care must be taken to not close windows in cases where the widget triggering the close is still in use.
        self.close()

    def refocus_widget(self, widget):
        widget.refocus()

    def __save_bounds(self):
        if self.__shown and self.__persistent_id:
            geometry, state = self.save()
            self.ui.set_persistent_string("{}/Geometry".format(self.__persistent_id), geometry)
            self.ui.set_persistent_string("{}/State".format(self.__persistent_id), state)

    def activation_changed(self, activated: bool) -> None:
        pass

    def size_changed(self, width: int, height: int) -> None:
        self.__save_bounds()

    def position_changed(self, x: int, y: int) -> None:
        self.__save_bounds()

    def key_pressed(self, key: UserInterface.Key) -> bool:
        return False

    def key_released(self, key: UserInterface.Key) -> bool:
        if key.modifiers.control and key.key:
            self._adjust_menus()
        return False

    def drag(self, mime_data: UserInterface.MimeData, thumbnail, hot_spot_x, hot_spot_y) -> None:
        self.__document_window.root_widget.drag(mime_data, thumbnail, hot_spot_x, hot_spot_y)

    @property
    def title(self) -> str:
        return self.__document_window.title

    @title.setter
    def title(self, value: str) -> None:
        self.__document_window.title = value

    def get_file_paths_dialog(self, title: str, directory: str, filter: str, selected_filter: str=None) -> (typing.List[str], str, str):
        return self.__document_window.get_file_paths_dialog(title, directory, filter, selected_filter)

    def get_file_path_dialog(self, title, directory, filter, selected_filter=None):
        return self.__document_window.get_file_path_dialog(title, directory, filter, selected_filter)

    def get_save_file_path(self, title, directory, filter, selected_filter=None):
        return self.__document_window.get_save_file_path(title, directory, filter, selected_filter)

    def create_dock_widget(self, widget: UserInterface.Widget, panel_id: str, title: str, positions: typing.Sequence[str], position: str) -> UserInterface.DockWidget:
        return self.__document_window.create_dock_widget(widget, panel_id, title, positions, position)

    def tabify_dock_widgets(self, dock_widget1, dock_widget2):
        return self.__document_window.tabify_dock_widgets(dock_widget1, dock_widget2)

    @property
    def screen_size(self):
        return self.__document_window.screen_size

    @property
    def screen_logical_dpi(self):
        return self.__document_window.screen_logical_dpi

    @property
    def screen_physical_dpi(self):
        return self.__document_window.screen_physical_dpi

    @property
    def display_scaling(self):
        return self.__document_window.display_scaling

    def get_font_metrics(self, font, text):
        return self.ui.get_font_metrics(font, text)

    @property
    def focus_widget(self):
        focus_widget = self.__document_window.focus_widget
        if focus_widget:
            return focus_widget
        for dock_widget in self.dock_widgets:
            focus_widget = dock_widget.focus_widget
            if focus_widget:
                return focus_widget
        return None

    @property
    def dock_widgets(self):
        return self.__document_window.dock_widgets

    def show(self, *, size: Geometry.IntSize=None, position: Geometry.IntPoint=None) -> None:
        self.__document_window.show(size=size, position=position)

    def add_menu(self, title: str, menu_id: str = None) -> UserInterface.Menu:
        return self.__document_window.add_menu(title, menu_id)

    def insert_menu(self, title: str, before_menu, menu_id: str = None) -> UserInterface.Menu:
        return self.__document_window.insert_menu(title, before_menu, menu_id)

    def create_sub_menu(self, title: str = None, menu_id: str = None) -> UserInterface.Menu:
        return self.ui.create_sub_menu(self.__document_window, title, menu_id)

    def create_context_menu(self):
        return self.ui.create_context_menu(self.__document_window)

    def restore(self, geometry: str, state: str) -> None:
        self.__document_window.restore(geometry, state)

    def save(self) -> (str, str):
        return self.__document_window.save()

    # tasks can be added in two ways, queued or added
    # queued tasks are guaranteed to be executed in the order queued.
    # added tasks are only executed if not replaced before execution.
    # added tasks do not guarantee execution order or execution at all.

    def add_task(self, key, task):
        assert task
        self.__periodic_set.add_task(key + str(id(self)), task)

    def clear_task(self, key):
        self.__periodic_set.clear_task(key + str(id(self)))

    def queue_task(self, task):
        assert task
        self.__periodic_queue.put(task)

    def clear_queued_tasks(self):
        self.__periodic_queue.clear_tasks()

    def handle_quit(self):
        self.app.exit()

    def _dispatch_any_to_focus_widget(self, method: str, *args, **kwargs) -> bool:
        focus_widget = self.focus_widget
        if focus_widget and focus_widget._dispatch_any(method, *args, **kwargs):
            return True
        if hasattr(self, method) and getattr(self, method)(*args, **kwargs):
            return True
        return False

    def build_menu(self, menu: typing.Optional[UserInterface.Menu], menu_descriptions: typing.Sequence[typing.Mapping]) -> None:
        for item_d in menu_descriptions:
            item_type = item_d["type"]
            if item_type == "menu":
                assert menu is None
                menu_id = item_d["menu_id"]
                menu_title = item_d["title"]
                menu_items = item_d["items"]
                new_menu = self.__document_window.get_menu(menu_id)
                if not new_menu:
                    new_menu = self.add_menu(menu_title, menu_id)
                    new_menu.on_about_to_show = functools.partial(self._menu_about_to_show, new_menu)
                setattr(self, "_" + menu_id + "_menu", new_menu)
                self.build_menu(new_menu, menu_items)
            elif item_type == "item":
                action_id = item_d["action_id"]
                action = actions.get(action_id)
                if action:
                    key_sequence = action_shortcuts.get(action_id, dict()).get("window")
                    role = getattr(action, "role", None)
                    menu.add_menu_item(action.action_name, functools.partial(self.perform_action, action_id),
                                       key_sequence=key_sequence, role=role, action_id=action_id)
                else:
                    logging.debug("Unregistered action {action_id}")
            elif item_type == "separator":
                menu.add_separator()
            elif item_type == "sub_menu":
                menu_id = item_d["menu_id"]
                menu_title = item_d["title"]
                menu_items = item_d["items"]
                new_menu = self.create_sub_menu(menu_title, menu_id)
                menu.add_sub_menu(menu_title, new_menu)
                new_menu.on_about_to_show = functools.partial(self._menu_about_to_show, new_menu)
                # setattr(self, "_" + menu_id + "_menu", new_menu)
                self.build_menu(new_menu, menu_items)

    def _get_action_context(self) -> typing.NamedTuple:
        focus_widget = self.focus_widget
        return ActionContext(self.app, self, focus_widget)

    def _apply_menu_state(self, action_id: str, action_context: typing.NamedTuple) -> None:
        menu_action = self.__document_window.get_menu_action(action_id)
        if menu_action:
            action = actions.get(menu_action.action_id)
            if action:
                title = action.get_action_name(action_context)
                enabled = action and action.is_enabled(action_context)
                checked = action and action.is_checked(action_context)
                menu_action.apply_state(UserInterface.MenuItemState(title=title, enabled=enabled, checked=checked))

    def perform_action(self, action_id: str) -> None:
        action = actions.get(action_id)
        if action:
            action.invoke(self._get_action_context())

    def _get_menu_item_state(self, command_id: str) -> typing.Optional[UserInterface.MenuItemState]:
        # if there is a specific menu item state for the command_id, use it
        # otherwise, if the handle method exists, return an enabled menu item
        # otherwise, don't handle
        handle_method = "handle_" + command_id
        menu_item_state_method = "get_" + command_id + "_menu_item_state"
        if hasattr(self, menu_item_state_method):
            menu_item_state = getattr(self, menu_item_state_method)()
            if menu_item_state:
                return menu_item_state
        if hasattr(self, handle_method):
            return UserInterface.MenuItemState(title=None, enabled=True, checked=False)
        return None

    def _get_focus_widget_menu_item_state(self, command_id: str) -> typing.Optional[UserInterface.MenuItemState]:
        focus_widget = self.focus_widget
        if focus_widget:
            menu_item_state = focus_widget._get_menu_item_state(command_id)
            if menu_item_state:
                return menu_item_state
        return self._get_menu_item_state(command_id)

    # standard menu items

    def _menu_about_to_show(self, menu: UserInterface.Menu) -> None:
        if menu.menu_id == "file":
            self._file_menu_about_to_show()
        elif menu.menu_id == "edit":
            self._edit_menu_about_to_show()
        elif menu.menu_id == "window":
            self._window_menu_about_to_show()
        else:
            action_context = self._get_action_context()
            for menu_action in menu.get_menu_actions():
                action = actions.get(menu_action.action_id)
                if action:
                    title = action.get_action_name(action_context)
                    enabled = action and action.is_enabled(action_context)
                    checked = action and action.is_checked(action_context)
                    menu_action.apply_state(UserInterface.MenuItemState(title=title, enabled=enabled, checked=checked))

    def _file_menu_about_to_show(self):
        action_context = self._get_action_context()
        self._apply_menu_state("window.close", action_context)
        self._apply_menu_state("window.page_setup", action_context)
        self._apply_menu_state("window.print", action_context)
        self._apply_menu_state("application.exit", action_context)
        # handle old style for backwards compatibility
        if self._close_action:
            self._close_action.enabled = True
        if self._page_setup_action:
            self._page_setup_action.apply_state(self._get_focus_widget_menu_item_state("page_setup"))
        if self._print_action:
            self._print_action.apply_state(self._get_focus_widget_menu_item_state("print"))
        if self._quit_action:
            self._quit_action.enabled = True

    def _edit_menu_about_to_show(self):
        action_context = self._get_action_context()
        self._apply_menu_state("window.undo", action_context)
        self._apply_menu_state("window.redo", action_context)
        self._apply_menu_state("window.cut", action_context)
        self._apply_menu_state("window.copy", action_context)
        self._apply_menu_state("window.paste", action_context)
        self._apply_menu_state("window.delete", action_context)
        self._apply_menu_state("window.select_all", action_context)
        # handle old style for backwards compatibility
        if self._undo_action:
            self._undo_action.apply_state(self._get_focus_widget_menu_item_state("undo"))
        if self._redo_action:
            self._redo_action.apply_state(self._get_focus_widget_menu_item_state("redo"))
        if self._cut_action:
            self._cut_action.apply_state(self._get_focus_widget_menu_item_state("cut"))
        if self._copy_action:
            self._copy_action.apply_state(self._get_focus_widget_menu_item_state("copy"))
        if self._paste_action:
            self._paste_action.apply_state(self._get_focus_widget_menu_item_state("paste"))
        if self._delete_action:
            self._delete_action.apply_state(self._get_focus_widget_menu_item_state("delete"))
        if self._select_all_action:
            self._select_all_action.apply_state(self._get_focus_widget_menu_item_state("select_all"))

    def _window_menu_about_to_show(self):
        action_context = self._get_action_context()
        self._apply_menu_state("window.minimize", action_context)
        self._apply_menu_state("window.zoom", action_context)
        self._apply_menu_state("window.bring_to_front", action_context)
        # handle old style for backwards compatibility
        if self._minimize_action:
            self._minimize_action.apply_state(self._get_focus_widget_menu_item_state("minimize"))
        if self._zoom_action:
            self._zoom_action.apply_state(self._get_focus_widget_menu_item_state("zoom"))
        if self._bring_to_front_action:
            self._bring_to_front_action.apply_state(self._get_focus_widget_menu_item_state("bring_to_front"))

    def _page_setup(self):
        self.perform_action("window.page_setup")

    def _print(self):
        self.perform_action("window.print")

    def _cut(self):
        self._dispatch_any_to_focus_widget("handle_cut")

    def _copy(self):
        self._dispatch_any_to_focus_widget("handle_copy")

    def _paste(self):
        self._dispatch_any_to_focus_widget("handle_paste")

    def _delete(self):
        self._dispatch_any_to_focus_widget("handle_delete")

    def _select_all(self):
        self._dispatch_any_to_focus_widget("handle_select_all")

    def _undo(self):
        self._dispatch_any_to_focus_widget("handle_undo")

    def _redo(self):
        self._dispatch_any_to_focus_widget("handle_redo")

    def _minimize(self):
        self._dispatch_any_to_focus_widget("handle_minimize")

    def _zoom(self):
        self._dispatch_any_to_focus_widget("handle_zoom")

    def _bring_to_front(self):
        self._dispatch_any_to_focus_widget("bring_to_front")


class AboutBoxAction(Action):
    action_id = "application.about"
    action_name = _("About...")
    action_role = "about"

    def invoke(self, context: ActionContext) -> None:
        if hasattr(context.window, "open_preferences"):
            context.window.show_about_box()
        elif hasattr(context.application, "open_preferences"):
            context.application.show_about_box()


class BringToFrontAction(Action):
    action_id = "window.bring_to_front"
    action_name = _("Bring to Front")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("bring_to_front")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "bring_to_front")


class CloseWindowAction(Action):
    action_id = "window.close"
    action_name = _("Close Window")

    def invoke(self, context: ActionContext) -> None:
        context.window.request_close()


class CopyAction(Action):
    action_id = "window.copy"
    action_name = _("Copy")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_copy")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_copy")


class CutAction(Action):
    action_id = "window.cut"
    action_name = _("Cut")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_cut")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_cut")


class DeleteAction(Action):
    action_id = "window.delete"
    action_name = _("Delete")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_delete")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_delete")


class ExitAction(Action):
    action_id = "application.exit"
    action_name = _("Exit")
    action_role = "quit"

    def invoke(self, context: ActionContext) -> None:
        context.application.exit()


class MinimizeAction(Action):
    action_id = "window.minimize"
    action_name = _("Minimize")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_minimize")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_minimize")


class PageSetupAction(Action):
    action_id = "window.page_setup"
    action_name = _("Page Setup")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_page_setup")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_page_setup")


class PasteAction(Action):
    action_id = "window.paste"
    action_name = _("Paste")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_paste")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_paste")


class PreferencesAction(Action):
    action_id = "application.preferences"
    action_name = _("Preferences...")
    action_role = "preferences"

    def invoke(self, context: ActionContext) -> None:
        if hasattr(context.window, "open_preferences"):
            context.window.open_preferences()
        elif hasattr(context.application, "open_preferences"):
            context.application.open_preferences()


class PrintAction(Action):
    action_id = "window.print"
    action_name = _("Print...")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_print")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_print")


class RedoAction(Action):
    action_id = "window.redo"
    action_name = _("Redo")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_redo")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_redo")


class SelectAllAction(Action):
    action_id = "window.select_all"
    action_name = _("Select All")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_select_all")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_select_all")


class UndoAction(Action):
    action_id = "window.undo"
    action_name = _("Undo")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_undo")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_undo")


class ZoomAction(Action):
    action_id = "window.zoom"
    action_name = _("Zoom")

    def invoke(self, context: ActionContext) -> None:
        context.window._dispatch_any_to_focus_widget("handle_zoom")

    def is_enabled(self, context: ActionContext) -> bool:
        return hasattr(context.window, "handle_zoom")


register_action(AboutBoxAction())
register_action(BringToFrontAction())
register_action(CloseWindowAction())
register_action(CopyAction())
register_action(CutAction())
register_action(DeleteAction())
register_action(ExitAction())
register_action(MinimizeAction())
register_action(PageSetupAction())
register_action(PasteAction())
register_action(PreferencesAction())
register_action(PrintAction())
register_action(SelectAllAction())
register_action(UndoAction())
register_action(RedoAction())
register_action(ZoomAction())

action_shortcuts_dict = {
    "application.exit": {"window": "quit"},
    "window.close": {"window": "close"},
    "window.print": {"window": "Ctrl+P"},
    "window.undo": {"window": "undo"},
    "window.redo": {"window": "redo"},
    "window.cut": {"window": "cut"},
    "window.copy": {"window": "copy"},
    "window.paste": {"window": "paste"},
    "window.delete": {"window": "delete"},
    "window.select_all": {"window": "select-all"},
}

register_action_shortcuts(action_shortcuts_dict)
