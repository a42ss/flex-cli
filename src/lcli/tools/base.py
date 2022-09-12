from lcli.app import App


class BaseTool:
    _app: App

    def __init__(self, app: App) -> None:
        self._app = app

    def h(self):
        """return the list of callable methods for autocomplete purpose"""
        method_names = [
            attr
            for attr in dir(self)
            if (callable(getattr(self, attr)) and attr[0] != "_" and attr != "h")
        ]
        return method_names


class ToolsException(Exception):
    pass
