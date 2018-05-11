import importlib
import os
import pkg_resources
import subprocess
import sys


def load_module_as_path(path):
    if os.path.isfile(path):
        dirname = os.path.dirname(path)
        module_name = os.path.splitext(os.path.basename(path))[0]
        sys.path.insert(0, dirname)
        module = importlib.import_module(module_name)
        return getattr(module, "main", None)
    return None


def load_module_as_package(package):
    try:
        module = importlib.import_module(package)
        main_fn = getattr(module, "main", None)
        if main_fn:
            return main_fn
    except ImportError:
        pass
    try:
        module = importlib.import_module(package + ".main")
        main_fn = getattr(module, "main", None)
        if main_fn:
            return main_fn
    except ImportError:
        pass
    return None


def load_module_local(path=None):
    try:
        if path:
            sys.path.insert(0, path)
        module = importlib.import_module("main")
        main_fn = getattr(module, "main", None)
        if main_fn:
            return main_fn
    except ImportError:
        pass
    return None


def bootstrap_main(args):
    """
    Main function explicitly called from the C++ code.
    Return the main application object.
    """
    version_info = sys.version_info
    if version_info.major != 3 or version_info.minor != 6:
        return None, "python36"
    main_fn = None
    if len(args) > 1:
        path = os.path.abspath(args[1])
        main_fn = load_module_as_path(path)
        main_fn = main_fn or load_module_as_package(args[1])
        main_fn = main_fn or load_module_local(path)
    if len(args) >= 0:
        main_fn = main_fn or load_module_local()
    if main_fn:
        return main_fn(args, {"pyqt": None}), None
    return None, "main"


def main():

    # first attempt to launch using nionui-launcher
    if pkg_resources.Environment()["nionui-tool"]:
        from nion.nionui_tool import command
        command.launch(sys.argv)
        return

    # next attempt to launch using pyqt
    success = False
    try:
        from PyQt5 import QtCore
        success = True
    except ImportError:
        print("Please install pyqt using pip or conda or use nionui-tool to launch.")

    if success:
        app, error = bootstrap_main(sys.argv)

        if app:
            app.run()
        else:
            print("Error: " + error)


if __name__ == '__main__':
    main()
