"""
A basic class to serve as the basis of a typical one window application.
"""
# standard libraries
import logging

# local libraries
# None


class Application:
    """A basic application class.

    Subclass this class and implement the start method. The start method should create a document window that will be
    the focus of the UI.

    Pass the desired user interface to the init method. Then call initialize and start.
    """

    def __init__(self, ui, *, on_start=None):
        self.ui = ui
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        self.window = None
        self.on_start = on_start

    def initialize(self):
        """Initialize. Separate from __init__ so that overridden methods can be called."""
        pass

    def deinitialize(self):
        self.ui.close()

    def start(self):
        """The start method should create a window that will be the focus of the UI."""
        if self.on_start:
            return self.on_start()
        raise NotImplemented()

    def exit(self):
        """The exit method should request to close or close the window."""
        raise NotImplemented()

    def periodic(self):
        """The periodic method can be overridden to implement periodic behavior."""
        pass


def make_ui(bootstrap_args):
    if "proxy" in bootstrap_args:
        from nion.ui import QtUserInterface
        proxy = bootstrap_args["proxy"]
        return QtUserInterface.QtUserInterface(proxy)
    elif "server" in bootstrap_args:
        from nion.ui import CanvasUI
        server = bootstrap_args["server"]
        return CanvasUI.CanvasUserInterface(server.draw, server.get_font_metrics)
    else:
        return None
