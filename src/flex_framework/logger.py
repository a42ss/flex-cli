import errno
import logging
import os
from typing import Dict, Optional, Type

import pinject

from .api.factory import Factory
from .api.proxy import ProxyContainer
from .config import Deployment
from .exceptions import FlexException


class Logger(logging.Logger):
    pass


class ProfilerLoggerProxy(ProxyContainer[Logger]):
    @pinject.annotate_arg("logger", "flex_framework.logger.profiler")
    def __init__(self, logger: Logger):
        self._subject = logger


class LoggerFactory(Factory):
    _deployment_config: Deployment

    @pinject.copy_args_to_internal_fields
    @pinject.annotate_arg("deployment_config", "flex_framework.config.deployment")
    def __init__(self, deployment_config: Deployment):
        super().__init__()

    def create(
        self, class_name: Type[Logger] = Logger, data: Optional[dict] = None
    ) -> Logger:
        if data is None:
            data = Dict[str, str]()
        return self.setup_logger(data)

    def setup_logger(self, data: dict) -> Logger:
        logger = logging.getLogger(data["name"])
        logger.setLevel(data["verbosity"])
        handler = logging.FileHandler(self.get_log_file(data["path"], data["file"]))
        handler.setLevel(data["verbosity"])
        handler.setFormatter(logging.Formatter(data["log_format"], data["date_format"]))
        logger.addHandler(handler)
        logger.__class__ = Logger
        if isinstance(logger, Logger):
            return logger
        raise FlexException("Unable to configure logger")

    def get_log_file(self, path: str, log_file: str):
        from pathlib import Path

        log_path = os.path.realpath(os.path.join(Path.home(), path))
        try:
            os.makedirs(log_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        return os.path.join(log_path, log_file)

    def create_by_logger_type(self, logger_id: str):
        logger_config = self.get_logger_config(logger_id)
        return self.setup_logger(logger_config)

    def get_logger_config(self, logger_id: str):
        logger_config: Dict[str, str] = {}
        logger_config_defaults = {
            "application_name": "flex-cli",
            "path": os.path.join(".flex-cli", "log"),
            "file": "application.log",
            "verbosity": logging.INFO,
            "log_format": "%(asctime)s " "%(levelname)-8s " "%(name)s: %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
        }
        if logger_id in self._deployment_config["logger"]:
            logger_config = self._deployment_config["logger"][logger_id]
        logger_config["name"] = logger_id

        return {**logger_config_defaults, **logger_config}


class ObjectManagerSpec(pinject.bindings.BindingSpec):
    deployment_config: Deployment

    def __init__(self, deployment_config: Deployment):
        self.deployment_config = deployment_config

    def configure(self, bind):
        logger_factory = LoggerFactory(self.deployment_config)

        self.bind_logger(bind, logger_factory, "application")
        self.bind_logger(bind, logger_factory, "debug")
        self.bind_logger(bind, logger_factory, "profiler")

    def bind_logger(self, bind, logger_factory, logger_id):
        application_logger_config = logger_factory.get_logger_config(logger_id)
        bind(
            "logger",
            in_scope=pinject.SINGLETON,
            annotated_with="flex_framework.logger." + logger_id,
            to_instance=logger_factory.create(data=application_logger_config),
        )
