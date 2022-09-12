import subprocess

from lcli.app import App
from lcli.tools import BaseTool


def _shell_execute(command: str, output: bool = False):
    if output:
        return subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
    else:
        return subprocess.call(command, shell=True)


class Git(BaseTool):
    """Git vcs interaction"""

    _command_name = "git"

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self._command_variables = self._app.get_config_object().get(
            ["commands_defaults", self._command_name], default={}
        )

    def pull(self):
        """Fetch changes from repo"""
        cmd = "git pull origin " + self.branch()
        _shell_execute(cmd)

    def fetch(self):
        """Fetch changes from repo"""
        _shell_execute("git fetch origin ")

    def commit(self, message: str = ""):
        """Commit changes with message or ask for it"""
        if message != "":
            cmd = 'git commit -m "' + message + '"'
        else:
            cmd = "git commit"
        _shell_execute(cmd)

    def add(self):
        """Add all changes to commit"""
        _shell_execute("git add .")

    def status(self):
        """Show changed files"""
        _shell_execute("git status")

    def diff(self):
        """Show changes"""
        _shell_execute("git diff")

    def save(self, message: str = ""):
        """Auto commit and push all changes"""
        self.add()
        if message != "":
            self.commit(message)
        else:
            self.commit(
                self.branch() + " " + self._command_variables.get("autocommit_message")
            )
        self.push()

    def amend(self):
        """Amend current changes"""
        self.add()
        _shell_execute("git commit --amend --reset-author")

    def cp(self, message: str = ""):
        """Auto commit and push all changes"""
        self.add()
        self.commit(message)
        self.push()

    def push(self, force: bool = False, remote: str = ""):
        """Push changes to remote repo"""
        cmd = "git push origin " + self.branch()
        if force:
            cmd += " -f"
        _shell_execute(cmd)

    def branch(self):
        """Push changes to remote repo"""
        cmd = "git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* (.*)/\\1/'"
        process = _shell_execute(cmd, True)
        out, err = process.communicate()
        if process.returncode == 0:
            return str(out.rstrip().decode())
        return ""

    def pwd(self):
        process = _shell_execute("pwd", True)
        out, err = process.communicate()
        if process.returncode == 0:
            return str(out.strip().decode())
        return ""

    def cli_info(self):
        """Provide cli headline information"""
        return [self.pwd(), self.branch()]
