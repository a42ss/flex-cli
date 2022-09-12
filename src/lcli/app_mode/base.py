from lcli.app_mode.exceptions import AppModeException


class AppModeBase:
    from lcli.app import App

    _app: App

    def __init__(self, app: App) -> None:
        self._app = app

    def run(self) -> None:
        """Run application in current mode"""
        raise AppModeException(
            "Application mode not implemented or is wrong configured."
        )
