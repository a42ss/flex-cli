from ..model import Config


class DirectoriesConfig(Config):
    @property
    def system_config(self) -> str:
        return self.get("system_config")

    @property
    def user_config(self) -> str:
        return self.get("user_config")

    @property
    def cwd_config(self) -> str:
        return self.get("cwd_config")
