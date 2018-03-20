# standard libraries
import gettext
import re

# local libraries
from nion.ui import Application
from nion.ui import Dialog
from nion.ui import Window
from nion.utils import Binding


_ = gettext.gettext


class DeclarativeUI:

    # ----: row
    # ----: column
    # ----: spacing
    # ----: stretch
    # ----: stack
    # ----: tab
    # ----: label
    # TODO: text edit
    # ----: line edit
    # TODO: scroll area
    # ----: group box
    # ----: status bar
    # TODO: tool tips
    # TODO: expander
    # TODO: border
    # ----: push button
    # ----: check box
    # ----: combo box
    # ----: radio buttons
    # TODO: splitter
    # TODO: image
    # ----: component
    # TODO: part
    # TODO: data view
    # TODO: list view
    # TODO: tree view
    # ----: slider
    # TODO: menus
    # TODO: context menu
    # ----: progress bar
    # TODO: key handler
    # TODO: canvas
    # TODO: dock panels
    # TODO: windows
    # TODO: thumbnails
    # TODO: display panels
    # TODO: periodic
    # ----: bindings
    # TODO: commands
    # TODO: standard dialog boxes, open, save, print, confirm
    # TODO: all static text (checkbox 'text') should be bindable

    def __init__(self):
        pass

    def create_column(self, *d_children, spacing=None, margin=None):
        d = {"type": "column"}
        if spacing is not None:
            d["spacing"] = spacing
        if margin is not None:
            d["margin"] = margin
        if len(d_children) > 0:
            children = d.setdefault("children", list())
            for d_child in d_children:
                children.append(d_child)
        return d

    def create_row(self, *d_children, spacing=None, margin=None):
        d = {"type": "row"}
        if spacing is not None:
            d["spacing"] = spacing
        if margin is not None:
            d["margin"] = margin
        if len(d_children) > 0:
            children = d.setdefault("children", list())
            for d_child in d_children:
                children.append(d_child)
        return d

    def create_spacing(self, size):
        return {"type": "spacing", "size": size}

    def create_stretch(self):
        return {"type": "stretch"}

    def create_tab(self, label, content):
        return {"type": "tab", "label": label, "content": content}

    def create_tabs(self, *d_tabs, name=None, current_index=None, on_current_index_changed=None):
        d = {"type": "tabs"}
        if len(d_tabs) > 0:
            children = d.setdefault("tabs", list())
            for d_child in d_tabs:
                children.append(d_child)
        if name is not None:
            d["name"] = name
        if current_index is not None:
            d["current_index"] = current_index
        if on_current_index_changed is not None:
            d["on_current_index_changed"] = on_current_index_changed
        return d

    def create_stack(self, *d_children, name=None, current_index=None, on_current_index_changed=None):
        d = {"type": "stack"}
        if len(d_children) > 0:
            children = d.setdefault("children", list())
            for d_child in d_children:
                children.append(d_child)
        if name is not None:
            d["name"] = name
        if current_index is not None:
            d["current_index"] = current_index
        if on_current_index_changed is not None:
            d["on_current_index_changed"] = on_current_index_changed
        return d

    def create_group(self, content, name=None, title=None, margin=None):
        d = {"type": "group", "content": content}
        if name is not None:
            d["name"] = name
        if title is not None:
            d["title"] = title
        if margin is not None:
            d["margin"] = margin
        return d

    def create_label(self, *, text: str=None, name=None):
        d = {"type": "text_label"}
        if text is not None:
            d["text"] = text
        if name is not None:
            d["name"] = name
        return d

    def create_line_edit(self, *,
                         text: str=None,
                         name=None,
                         editable=None,
                         placeholder_text=None,
                         clear_button_enabled=None,
                         on_editing_finished=None,
                         on_escape_pressed=None,
                         on_return_pressed=None,
                         on_key_pressed=None,
                         on_text_edited=None):
        d = {"type": "line_edit"}
        if text is not None:
            d["text"] = text
        if name is not None:
            d["name"] = name
        if editable is not None:
            d["editable"] = editable
        if placeholder_text is not None:
            d["placeholder_text"] = placeholder_text
        if clear_button_enabled is not None:
            d["clear_button_enabled"] = clear_button_enabled
        if on_editing_finished is not None:
            d["on_editing_finished"] = on_editing_finished
        if on_escape_pressed is not None:
            d["on_escape_pressed"] = on_escape_pressed
        if on_return_pressed is not None:
            d["on_return_pressed"] = on_return_pressed
        if on_key_pressed is not None:
            d["on_key_pressed"] = on_key_pressed
        if on_text_edited is not None:
            d["on_text_edited"] = on_text_edited
        return d

    def create_push_button(self, *, text: str=None, name=None, on_clicked=None):
        d = {"type": "push_button"}
        if text is not None:
            d["text"] = text
        if name is not None:
            d["name"] = name
        if on_clicked is not None:
            d["on_clicked"] = on_clicked
        return d

    def create_check_box(self, *,
                         text: str=None,
                         name=None,
                         checked=None,
                         check_state=None,
                         tristate=None,
                         on_checked_changed=None,
                         on_check_state_changed=None):
        d = {"type": "check_box"}
        if text is not None:
            d["text"] = text
        if checked is not None:
            d["checked"] = checked
        if check_state is not None:
            d["check_state"] = check_state
        if tristate is not None:
            d["tristate"] = tristate
        if name is not None:
            d["name"] = name
        if on_checked_changed is not None:
            d["on_checked_changed"] = on_checked_changed
        if on_check_state_changed is not None:
            d["on_check_state_changed"] = on_check_state_changed
        return d

    def create_combo_box(self, *,
                         name=None,
                         items=None,
                         items_ref=None,
                         current_index=None,
                         on_current_index_changed=None):
        d = {"type": "combo_box"}
        if name is not None:
            d["name"] = name
        if items is not None:
            d["items"] = items
        if items_ref is not None:
            d["items_ref"] = items_ref
        if current_index is not None:
            d["current_index"] = current_index
        if on_current_index_changed is not None:
            d["on_current_index_changed"] = on_current_index_changed
        return d

    def create_radio_button(self, *,
                            name=None,
                            text=None,
                            value=None,
                            group_value=None):
        d = {"type": "radio_button"}
        if name is not None:
            d["name"] = name
        if text is not None:
            d["text"] = text
        if value is not None:
            d["value"] = value
        if group_value is not None:
            d["group_value"] = group_value
        return d

    def create_slider(self, *,
                      name=None,
                      value=None,
                      minimum=None,
                      maximum=None,
                      on_value_changed=None,
                      on_slider_pressed=None,
                      on_slider_released=None,
                      on_slider_moved=None,
                      ):
        d = {"type": "slider"}
        if name is not None:
            d["name"] = name
        if value is not None:
            d["value"] = value
        if minimum is not None:
            d["minimum"] = minimum
        if maximum is not None:
            d["maximum"] = maximum
        if on_value_changed is not None:
            d["on_value_changed"] = on_value_changed
        if on_slider_pressed is not None:
            d["on_slider_pressed"] = on_slider_pressed
        if on_slider_released is not None:
            d["on_slider_released"] = on_slider_released
        if on_slider_moved is not None:
            d["on_slider_moved"] = on_slider_moved
        return d

    def create_progress_bar(self, *,
                      name=None,
                      value=None,
                      minimum=None,
                      maximum=None):
        d = {"type": "progress_bar"}
        if name is not None:
            d["name"] = name
        if value is not None:
            d["value"] = value
        if minimum is not None:
            d["minimum"] = minimum
        if maximum is not None:
            d["maximum"] = maximum
        return d

    def create_modeless_dialog(self, content, *, title: str=None, resources=None, margin=None):
        d = {"type": "modeless_dialog", "content": content}
        if title is not None:
            d["title"] = title
        if margin is not None:
            d["margin"] = margin
        if resources is not None:
            d["resources"] = resources
        return d

    def create_window(self, content, *, title: str=None, resources=None, margin=None):
        d = {"type": "window", "content": content}
        if title is not None:
            d["title"] = title
        if margin is not None:
            d["margin"] = margin
        if resources is not None:
            d["resources"] = resources
        return d

    def define_component(self, content, create_handler_method_name, events=None):
        d = {"type": "component", "content": content, "create_handler_method_name": create_handler_method_name}
        if events is not None:
            d["events"] = events
        return d

    def create_component_instance(self, identifier, properties=None, **kwargs):
        properties = properties if properties is not None else dict()
        d = {"type": "component", "identifier": identifier, "properties": properties}
        for k, v in kwargs.items():
            d[k] = v
        return d


def connect_name(widget, d, handler):
    name = d.get("name", None)
    if name:
        setattr(handler, name, widget)


def connect_string_value(widget, d, handler, property, finishes):
    """Connects a value in the property, but also allows binding.

    A value means the value for the property is directly contained in the string.
    """
    v = d.get(property)
    m = re.match("^@binding\((.+)\)$", v if v else "")
    # print(f"{v}, {m}, {m.group(1) if m else 'NA'}")
    if m:
        b = m.group(1)
        parts = [p.strip() for p in b.split(',')]
        def finish_binding():
            handler_property_path = parts[0].split('.')
            source = handler
            for p in handler_property_path[:-1]:
                source = getattr(source, p.strip())
            converter = None
            for part in parts:
                if part.startswith("converter="):
                    converter = getattr(handler, part[len("converter="):])
            binding = Binding.PropertyBinding(source, handler_property_path[-1].strip(), converter=converter)
            getattr(widget, "bind_" + property)(binding)
        finishes.append(finish_binding)
    else:
        setattr(widget, property, v)


def connect_reference_value(widget, d, handler, property, finishes, binding_name=None):
    """Connects a reference to the property, but also allows binding.

    A reference means the property specifies a property in the handler.
    """
    binding_name = binding_name if binding_name else property
    v = d.get(property)
    m = re.match("^@binding\((.+)\)$", v if v else "")
    # print(f"{v}, {m}, {m.group(1) if m else 'NA'}")
    if m:
        b = m.group(1)
        parts = [p.strip() for p in b.split(',')]
        def finish_binding():
            handler_property_path = parts[0].split('.')
            source = handler
            for p in handler_property_path[:-1]:
                source = getattr(source, p.strip())
            converter = None
            for part in parts:
                if part.startswith("converter="):
                    converter = getattr(handler, part[len("converter="):])
            binding = Binding.PropertyBinding(source, handler_property_path[-1].strip(), converter=converter)
            getattr(widget, "bind_" + binding_name)(binding)
        finishes.append(finish_binding)
    elif v is not None:
        setattr(widget, binding_name, getattr(handler, v))


def connect_event(widget, source, d, handler, event_str, arg_names):
    event_method_name = d.get(event_str, None)
    if event_method_name:
        event_fn = getattr(handler, event_method_name)
        if event_fn:
            def trampoline(*args, **kwargs):
                combined_args = dict()
                for arg_name, arg in zip(arg_names, args):
                    combined_args[arg_name] = arg
                combined_args.update(kwargs)
                event_fn(widget, **combined_args)
            setattr(source, event_str, trampoline)
        else:
            print("WARNING: '" + event_str + "' method " + event_method_name + " not found in handler.")


def run_window(app, d, handler):
    ui = app.ui
    d_type = d.get("type")
    if d_type == "window":
        title = d.get("title", _("Untitled"))
        margin = d.get("margin")
        persistent_id = d.get("persistent_id")
        content = d.get("content")
        resources = d.get("resources", dict())
        for k, v in resources.items():
            resources[k] = v
        if not hasattr(handler, "resources"):
            handler.resources = resources
        else:
            handler.resources.update(resources)
        finishes = list()
        window = Window.Window(ui, app=app, persistent_id=persistent_id)
        outer_row = ui.create_row_widget()
        outer_column = ui.create_column_widget()
        inner_content = construct(ui, window, content, handler, finishes)
        if margin is not None:
            outer_row.add_spacing(margin)
            outer_column.add_spacing(margin)
        outer_column.add(inner_content)
        outer_row.add(outer_column)
        if margin is not None:
            outer_row.add_spacing(margin)
            outer_column.add_spacing(margin)
        window.attach_widget(outer_row)
        window.show()
        for finish in finishes:
            finish()
        if handler and hasattr(handler, "init_handler"):
            handler.init_handler()
        def close_handler():
            if handler and hasattr(handler, "close"):
                handler.close()
        window.on_close = close_handler
        return window


def construct_margin(ui, content, margin):
    if margin:
        column = ui.create_column_widget()
        column.add_spacing(margin)
        column.add(content)
        column.add_spacing(margin)
        row = ui.create_row_widget()
        row.add_spacing(margin)
        row.add(column)
        row.add_spacing(margin)
        content = row
    return content


def construct(ui, window, d, handler, finishes=None):
    d_type = d.get("type")
    if d_type == "modeless_dialog":
        title = d.get("title", _("Untitled"))
        margin = d.get("margin")
        persistent_id = d.get("persistent_id")
        content = d.get("content")
        resources = d.get("resources", dict())
        for k, v in resources.items():
            resources[k] = v
        if not hasattr(handler, "resources"):
            handler.resources = resources
        else:
            handler.resources.update(resources)
        finishes = list()
        dialog = Dialog.ActionDialog(ui, title, app=window.app, parent_window=window, persistent_id=persistent_id)
        dialog._create_menus()
        outer_row = ui.create_row_widget()
        outer_column = ui.create_column_widget()
        inner_content = construct(ui, window, content, handler, finishes)
        if margin is not None:
            outer_row.add_spacing(margin)
            outer_column.add_spacing(margin)
        outer_column.add(inner_content)
        outer_row.add(outer_column)
        if margin is not None:
            outer_row.add_spacing(margin)
            outer_column.add_spacing(margin)
        dialog.content.add(outer_row)
        for finish in finishes:
            finish()
        if handler and hasattr(handler, "init_handler"):
            handler.init_handler()
        def close_handler():
            if handler and hasattr(handler, "close"):
                handler.close()
        dialog.on_close = close_handler
        return dialog
    elif d_type == "column":
        column_widget = ui.create_column_widget()
        spacing = d.get("spacing")
        margin = d.get("margin")
        children = d.get("children", list())
        first = True
        for child in children:
            if not first and spacing is not None:
                column_widget.add_spacing(spacing)
            if child.get("type") == "spacing":
                column_widget.add_spacing(child.get("size", 0))
            elif child.get("type") == "stretch":
                column_widget.add_stretch()
            else:
                column_widget.add(construct(ui, window, child, handler, finishes))
            first = False
        return construct_margin(ui, column_widget, margin)
    elif d_type == "row":
        row_widget = ui.create_row_widget()
        spacing = d.get("spacing")
        margin = d.get("margin")
        children = d.get("children", list())
        first = True
        for child in children:
            if not first and spacing is not None:
                row_widget.add_spacing(spacing)
            if child.get("type") == "spacing":
                row_widget.add_spacing(child.get("size", 0))
            elif child.get("type") == "stretch":
                row_widget.add_stretch()
            else:
                row_widget.add(construct(ui, window, child, handler, finishes))
            first = False
        return construct_margin(ui, row_widget, margin)
    elif d_type == "text_label":
        widget = ui.create_label_widget()
        if handler:
            connect_string_value(widget, d, handler, "text", finishes)
            connect_name(widget, d, handler)
        return widget
    elif d_type == "line_edit":
        editable = d.get("editable", None)
        placeholder_text = d.get("placeholder_text", None)
        clear_button_enabled = d.get("clear_button_enabled", None)
        widget = ui.create_line_edit_widget()
        if editable is not None:
            widget.editable = editable
        if placeholder_text is not None:
            widget.placeholder_text = placeholder_text
        if clear_button_enabled is not None:
            widget.clear_button_enabled = clear_button_enabled
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "text", finishes)
            connect_event(widget, widget, d, handler, "on_editing_finished", ["text"])
            connect_event(widget, widget, d, handler, "on_escape_pressed", [])
            connect_event(widget, widget, d, handler, "on_return_pressed", [])
            connect_event(widget, widget, d, handler, "on_key_pressed", ["key"])
            connect_event(widget, widget, d, handler, "on_text_edited", ["text"])
        return widget
    elif d_type == "push_button":
        text = d.get("text", None)
        widget = ui.create_push_button_widget(text)
        if handler:
            connect_name(widget, d, handler)
            connect_event(widget, widget, d, handler, "on_clicked", [])
        return widget
    elif d_type == "check_box":
        text = d.get("text", None)
        checked = d.get("checked", None)
        check_state = d.get("check_state", None)
        tristate = d.get("tristate", None)
        widget = ui.create_check_box_widget(text)
        if tristate is not None:
            widget.tristate = tristate
        if check_state is not None:
            widget.check_state = check_state
        if checked is not None:
            widget.checked = checked
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "checked", finishes)
            connect_reference_value(widget, d, handler, "check_state", finishes)
            connect_event(widget, widget, d, handler, "on_checked_changed", ["checked"])
            connect_event(widget, widget, d, handler, "on_check_state_changed", ["check_state"])
        return widget
    elif d_type == "combo_box":
        items = d.get("items", None)
        widget = ui.create_combo_box_widget(items=items)
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "current_index", finishes)
            connect_reference_value(widget, d, handler, "items_ref", finishes, binding_name="items")
            connect_event(widget, widget, d, handler, "on_current_index_changed", ["current_index"])
        return widget
    elif d_type == "radio_button":
        text = d.get("text", None)
        value = d.get("value", None)
        widget = ui.create_radio_button_widget(text)
        widget.value = value
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "group_value", finishes)
        return widget
    elif d_type == "slider":
        minimum = d.get("minimum", 0)
        maximum = d.get("maximum", 100)
        widget = ui.create_slider_widget()
        widget.minimum = minimum
        widget.maximum = maximum
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "value", finishes)
            connect_event(widget, widget, d, handler, "on_value_changed", ["value"])
            connect_event(widget, widget, d, handler, "on_slider_pressed", [])
            connect_event(widget, widget, d, handler, "on_slider_released", [])
            connect_event(widget, widget, d, handler, "on_slider_moved", ["value"])
        return widget
    elif d_type == "progress_bar":
        minimum = d.get("minimum", 0)
        maximum = d.get("maximum", 100)
        widget = ui.create_progress_bar_widget(properties={"height": 18, "min-width": 64})
        widget.minimum = minimum
        widget.maximum = maximum
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "value", finishes)
        return widget
    elif d_type == "tabs":
        widget = ui.create_tab_widget()
        for tab in d.get("tabs", list()):
            widget.add(construct(ui, window, tab["content"], handler, finishes), tab["label"])
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "current_index", finishes)
            connect_event(widget, widget, d, handler, "on_current_index_changed", ["current_index"])
        return widget
    elif d_type == "stack":
        widget = ui.create_stack_widget()
        for child in d.get("children", list()):
            widget.add(construct(ui, window, child, handler, finishes))
        if handler:
            connect_name(widget, d, handler)
            connect_reference_value(widget, d, handler, "current_index", finishes)
            connect_event(widget, widget, d, handler, "on_current_index_changed", ["current_index"])
        return widget
    elif d_type == "group":
        widget = ui.create_group_widget()
        margin = d.get("margin")
        content = d.get("content")
        outer_row = ui.create_row_widget()
        outer_column = ui.create_column_widget()
        inner_content = construct(ui, window, content, handler, finishes)
        if margin is not None:
            outer_row.add_spacing(margin)
            outer_column.add_spacing(margin)
        outer_column.add(inner_content)
        outer_row.add(outer_column)
        if margin is not None:
            outer_row.add_spacing(margin)
            outer_column.add_spacing(margin)
        widget.add(outer_row)
        if handler:
            connect_name(widget, d, handler)
            connect_string_value(widget, d, handler, "title", finishes)
        return widget
    elif d_type == "component":
        # a component needs to be registered before it is instantiated.
        # look up the identifier in the handler resoureces.
        identifier = d.get("identifier", None)
        component = handler.resources.get(identifier)
        if component:
            assert component.get("type") == "component"
            # the component will have a content portion, which is just a widget description.
            # it will also have a function to create its handler. finally the component will
            # have a list of events that to be connected.
            content = component.get("content")
            create_handler_method_name = component.get("create_handler_method_name")
            events = component.get("events", list())
            # create the handler first, but don't initialize it.
            component_handler = getattr(handler, create_handler_method_name)() if create_handler_method_name and hasattr(handler, create_handler_method_name) else None
            if component_handler:
                # set properties in the component from the properties dict
                for k, v in d.get("properties", dict()).items():
                    # print(f"setting property {k} to {v}")
                    setattr(component_handler, k, v)
            # now construct the widget
            widget = construct(ui, window, content, component_handler, finishes)
            if handler:
                # connect the name to the handler if desired
                connect_name(widget, d, handler)
                # since the handler is custom to the widget, make a way to retrieve it from the widget
                widget.handler = component_handler
                if component_handler and hasattr(component_handler, "init_component"):
                    component_handler.init_component()
                # connect events
                for event in events:
                    # print(f"connecting {event['event']} ({event['parameters']})")
                    connect_event(widget, component_handler, d, handler, event["event"], event["parameters"])
            return widget
    return None

def run_ui(args, bootstrap_args, d, handler):

    def start():
        run_window(app, d, handler)
        return True

    app = Application.Application(Application.make_ui(bootstrap_args), on_start=start)
    app.initialize()
    return app
