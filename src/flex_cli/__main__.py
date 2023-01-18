from typing import Optional

from . import EXECUTABLE_NAME
from .application import ApplicationBootstrap
from .application.flex_cli import FlexCli
from .etc.config import params


def main(init_params: Optional[dict] = None):
    bootstrap = ApplicationBootstrap.create_with_file_name(EXECUTABLE_NAME, params)
    application = bootstrap.create_application(FlexCli)
    bootstrap.run(application)


if __name__ == "__main__":
    main({})
