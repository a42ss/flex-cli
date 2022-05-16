import sys
from invoke import run, task


@task
def configure(ctx):
    """
    Instructions for preparing package for development.
    """

    run("%s -m pip install .[dev] -r requirements.txt" % sys.executable)

@task
def install(ctx):
    """
    Instructions for preparing package for development.
    """

    run("%s -m pip install -r requirements.txt" % sys.executable)
    run("%s -m pip install . --user" % sys.executable)


@task
def coverage(ctx):
    """
    Instructions for preparing package for development.
    """
    run("pytest --cov=./src/lcli/ .")


@task
def test(ctx):
    """
    Instructions for preparing package for development.
    """
    run("pytest")


@task
def docs(ctx):
    """
    Build md readme into rst in docs
    """
    run("m2r README.md --dry-run | tee docs/README.rst")

