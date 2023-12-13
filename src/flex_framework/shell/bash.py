import glob
import json
import os
import subprocess
import sys

import pinject
from dotenv import set_key as env_set_key

from ..environment.manager import Environment as EnvironmentManager
from .proxy import SimpleShellProxy


class BashEmulator(SimpleShellProxy):
    def emulate_bash(self):
        # flake8: noqa

        bash_command_string = (
            "/usr/bin/env bash --init-file <(echo '"
            ". $HOME/.bashrc; "
            'export PATH="' + self.env["FLEX_SHELL_PROXY_LOCAL_PATH"] + ':$PATH";'
            ". " + os.path.dirname(__file__) + "/.bashrc"
            "') -i -O expand_aliases "
        )
        other_args = " ".join(sys.argv[1:])
        if len(other_args) > 2:
            bash_command_string += " -c "

        return self.execute(bash_command_string)

    def run_bash(self):
        bash_command_string = "/usr/bin/env bash -i"
        other_args = " ".join(sys.argv[1:])
        if len(other_args) > 2:
            bash_command_string += " -c "

        return self.execute(bash_command_string)


class BashEmulatorFlexAware(BashEmulator):
    class Const:
        FLEX_SHELL_ENV_NAME: str = "FLEX_SHELL_ENV_NAME"
        FLEX_BASH_PROXY: str = "FLEX_BASH_PROXY"
        FLEX_BASH_PROXY_META: str = "FLEX_BASH_PROXY_META"
        FLEX_BASH_PROXY_DIR: str = os.path.join(
            os.getcwd(), ".flex-cli", "cache", "bin"
        )

    env_name: str = "dev"

    @pinject.copy_args_to_internal_fields
    def __init__(self, environment: EnvironmentManager, env_path_to_remove=None):
        super(BashEmulatorFlexAware, self).__init__(
            environment=environment, env_path_to_remove=None
        )
        self.env_name = self.get_env_name()

    def get_env_name(self):
        env_name = self.env.get(self.Const.FLEX_SHELL_ENV_NAME)
        if env_name is not None:
            return env_name

        path = os.path.join(os.getcwd(), "env")
        default__root_env_file = os.path.join(os.getcwd(), ".env")
        default_env_file = os.path.join(path, ".env")
        env_vars_root = self.read_environment_variables(default__root_env_file)
        env_vars = self.read_environment_variables(default_env_file)
        env_vars.update(env_vars_root)
        self.env[self.Const.FLEX_SHELL_ENV_NAME] = "local"
        for key, value in env_vars.items():
            self.env[key] = value

        return self.env.get(self.Const.FLEX_SHELL_ENV_NAME)

    def emulate_bash(self):
        while True:
            self.clean_cache_directory()
            self.env_name = self.get_env_name()
            if not "FLEX_CLI" in self.env:
                self.run_bash()
                return
            self.env = os.environ.copy()
            self.init_env_variables()
            self.init_bash_proxy_commands()
            self.save_env_to_local_cache_file()
            exit_code = super().emulate_bash()

            if exit_code != 115:
                break
            if "FLEX_RELOAD_FLAG" in os.environ:
                os.environ.pop("FLEX_RELOAD_FLAG")
            if "FLEX_RELOAD_FLAG" in self.env:
                self.env.pop("FLEX_RELOAD_FLAG")

            if (
                self.Const.FLEX_SHELL_ENV_NAME in self.env
                and self.env[self.Const.FLEX_SHELL_ENV_NAME]
            ):
                self.env.pop(self.Const.FLEX_SHELL_ENV_NAME)
            print("Flex console have been triggered to force reload. (exit code 115)")

    def get_env_files(self) -> list:
        path = os.path.join(os.getcwd(), "env", self.env_name)
        env_files = []
        default_env_file = os.path.join(path, ".env")
        base_env_file = os.path.join(os.getcwd(), "env", ".env")
        if os.path.isfile(base_env_file):
            env_files.append(base_env_file)
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
            os.path.join(os.getcwd(), ".flex-cli", "cache", "bin"),
            os.path.join(os.getcwd(), "bin"),
            os.path.join(os.getcwd(), "bin", "stack"),
        ]

    def read_environment_variables(self, file: str):
        if not os.path.isfile(file):
            return {}
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

    def clean_cache_directory(self):
        os.system("rm -rf " + self.Const.FLEX_BASH_PROXY_DIR)

    def init_bash_proxy_commands(self):
        self.clean_cache_directory()
        os.makedirs(self.Const.FLEX_BASH_PROXY_DIR)
        bash_proxy_commands = self.env.get(self.Const.FLEX_BASH_PROXY)
        if bash_proxy_commands is None:
            bash_proxy_commands = ""
        try:
            bash_proxy_meta = json.loads(self.env.get(self.Const.FLEX_BASH_PROXY_META))
        except Exception as e:
            bash_proxy_meta = {}
            pass
        for bash_proxy_command in bash_proxy_commands.split(":"):
            if type(bash_proxy_meta) == dict and bash_proxy_command in bash_proxy_meta:
                bash_proxy_command_safe = bash_proxy_command.replace("-", "_")
                if "container" in bash_proxy_meta[bash_proxy_command]:
                    self.env[
                        "FLEX_CONTAINER_" + bash_proxy_command_safe.upper()
                    ] = bash_proxy_meta[bash_proxy_command]["container"]
                    self.env[
                        "FLEX_CONTAINER_EXECUTABLE_" + bash_proxy_command_safe.upper()
                    ] = bash_proxy_meta[bash_proxy_command]["executable"]
                    self.execute(
                        "ln -s "
                        + os.path.join(os.path.dirname(__file__), "bash_proxy_symlink")
                        + " "
                        + os.path.join(
                            self.Const.FLEX_BASH_PROXY_DIR, bash_proxy_command
                        ),
                        append_arguments=False,
                    )
                if "alias" in bash_proxy_meta[bash_proxy_command]:
                    self.env[
                        "FLEX_ALIAS_" + bash_proxy_command_safe.upper()
                    ] = bash_proxy_meta[bash_proxy_command]["alias"]
                    self.execute(
                        "ln -s "
                        + os.path.join(os.path.dirname(__file__), "bash_alias_symlink")
                        + " "
                        + os.path.join(
                            self.Const.FLEX_BASH_PROXY_DIR, bash_proxy_command
                        ),
                        append_arguments=False,
                    )

    def save_env_to_local_cache_file(self):
        for key in self.env:
            save_key = False
            if key == "PATH":
                env_set_key(
                    os.path.join(self.Const.FLEX_BASH_PROXY_DIR, "PATH-flex.env"),
                    key,
                    self.env[key],
                )
                env_set_key(
                    os.path.join(self.Const.FLEX_BASH_PROXY_DIR, "PATH-original.env"),
                    key,
                    os.environ[key],
                )
                continue
            if key in os.environ:
                if os.environ[key] != self.env[key]:
                    save_key = True
            else:
                save_key = True
            if save_key:
                env_set_key(
                    os.path.join(self.Const.FLEX_BASH_PROXY_DIR, ".env"),
                    key,
                    self.env[key],
                )
