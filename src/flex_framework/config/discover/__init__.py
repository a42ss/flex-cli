import os

import pinject

from ..deployment import Deployment


class ConfigDirectories:
    _deployment_config: Deployment

    @pinject.annotate_arg("deployment_config", "flex_framework.config.deployment")
    def __init__(self, deployment_config: Deployment):
        self._deployment_config = deployment_config

    def get_available_directories(self):
        result = []
        directories = [
            self._deployment_config.dirs.system_config,
            self._deployment_config.dirs.user_config,
            self._deployment_config.dirs.cwd_config,
        ]

        for directory in directories:
            directory = os.path.realpath(directory)
            if not os.access(directory, os.X_OK):
                continue
            result.append(directory)

        return result
