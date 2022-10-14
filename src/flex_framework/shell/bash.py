import glob
import os
import subprocess

import pinject

from flex_framework.shell.proxy import SimpleShellProxy

from ..environment.manager import Environment as EnvironmentManager


class BashEmulator(SimpleShellProxy):
    def emulate_bash(self):
        # flake8: noqa
        bash_command_string = (
            "/usr/bin/env bash --init-file <(echo '"
            ". $HOME/.bashrc; "
            'export PATH="' + self.env["FLEX_SHELL_PROXY_LOCAL_PATH"] + ':$PATH"; '
            'export PS1="\[\e[m\]\[\e[0;31m\]\$(echo "[\$FLEX_SHELL_PROXY_ENV_NAME]")\[\e[m\] \w $PS1"; '
            'alias reload="envsubst < ./env/.env.template > ./env/.env; exit 115";'
            'alias switch_local="export FLEX_SHELL_PROXY_ENV_NAME=local; reload";'
            'alias switch_dev="export FLEX_SHELL_PROXY_ENV_NAME=dev; reload"'
            "')"
        )
        return self.execute(bash_command_string)


class BashEmulatorFlexAware(BashEmulator):
    class Const:
        FLEX_SHELL_ENV_NAME: str = "FLEX_SHELL_ENV_NAME"

    env_name: str = "dev"

    @pinject.copy_args_to_internal_fields
    def __init__(self, environment: EnvironmentManager, env_path_to_remove=None):
        super(BashEmulatorFlexAware, self).__init__(
            environment=environment, env_path_to_remove=None
        )
        self.env_name = self.get_env_name()

    def get_env_name(self):
        path = os.path.join(os.getcwd(), "env")
        default_env_file = os.path.join(path, ".env")
        env_vars = self.read_environment_variables(default_env_file)
        for key, value in env_vars.items():
            self.env[key] = value

        env_name = self.env.get(self.Const.FLEX_SHELL_ENV_NAME)
        if env_name is None:
            return "dev"
        return env_name

    def emulate_bash(self):
        while True:
            self.env_name = self.get_env_name()
            self.env = os.environ.copy()
            self.init_env_variables()
            exit_code = super().emulate_bash()

            if exit_code != 115:
                break

            print("Flex console have been triggered to force reload. (exit code 115)")

    def get_env_files(self) -> list:
        path = os.path.join(os.getcwd(), "env", self.env_name)
        env_files = []
        default_env_file = os.path.join(path, ".env")
        if os.path.isfile(default_env_file):
            env_files.append(default_env_file)

        for file in glob.glob("*.env", root_dir=path, recursive=True):
            env_files.append(os.path.join(path, file))
        return env_files

    def init_env_variables(self):
        for file in self.get_env_files():
            env_vars = self.read_environment_variables(file)
            for key, value in env_vars.items():
                self.env[key] = value

        self.env["FLEX_SHELL_PROXY_ENV_NAME"] = self.env_name
        self.env["FLEX_SHELL_PROXY_LOCAL_PATH"] = ":".join(
            self.get_local_path_entries()
        )
        self.env["PATH"] = (
            self.env["FLEX_SHELL_PROXY_LOCAL_PATH"] + ":" + self.env["PATH"]
        )

    def get_local_path_entries(self) -> list:
        return [
            os.path.join(os.getcwd(), "bin"),
            os.path.join(os.getcwd(), "bin", "stack"),
        ]

    def read_environment_variables(self, file: str):
        full_env_vars = subprocess.check_output(
            'env -i bash --noprofile --norc -c "set -o allexport; source '
            + file
            + '; set +o allexport; printenv"',
            shell=True,
            env=self.env,
        ).decode("utf-8")
        empty_env_vars = subprocess.check_output(
            '/usr/bin/env bash -c "env"', shell=True, env=self.env
        ).decode("utf-8")

        original_env_vars_dict = {}
        for var_line in empty_env_vars.split("\n"):
            key_pair = var_line.split("=", 1)
            if len(key_pair) == 2:
                original_env_vars_dict[key_pair[0]] = key_pair[1]

        full_file_env_vars_dict = {}
        for var_line in full_env_vars.split("\n"):
            key_pair = var_line.split("=", 1)
            if len(key_pair) == 2:
                if (
                    key_pair[0] not in original_env_vars_dict
                    or original_env_vars_dict[key_pair[0]] != key_pair[1]
                ):
                    full_file_env_vars_dict[key_pair[0]] = key_pair[1]

        return full_file_env_vars_dict
