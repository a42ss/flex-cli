from flex_framework.api.handler import HandlerInterface, get_handler

from .env import params as flex_global_env_parameters


def extend_env_variables(local_params: dict, default_handler=None):
    if default_handler is not None:
        local_params[HandlerInterface.Const.DEFAULT_HANDLER] = get_handler(
            default_handler
        )

    return {**flex_global_env_parameters, **local_params}
