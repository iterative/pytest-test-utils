"""Automation using nox.
"""
import glob
import sys

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = "lint", "tests", "compat"
locations = "pytest_test_utils", "tests.py"


@nox.session(
    python=["3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "pypy3.8", "pypy3.9"]
)
def tests(session: nox.Session) -> None:
    session.install(".[tests]")
    # `pytest --cov` will start coverage after pytest
    # so we need to use `coverage`.
    session.run("coverage", "run", "-m", "pytest")
    session.run("coverage", "report", "--show-missing", "--skip-covered")


@nox.session(python=["3.7", "3.8"])
@nox.parametrize("pytest", ["3.9.1", "4.0", "5.0", "6.0", "7.0"])
def compat(session: nox.Session, pytest: str) -> None:
    session.install(".[tests]")
    session.install(f"pytest=={pytest}")
    session.run("coverage", "run", "-m", "pytest", "tests.py")


@nox.session
def lint(session: nox.Session) -> None:
    session.install("pre-commit")
    session.install("-e", ".[dev]")

    if session.posargs:
        args = session.posargs + ["--all-files"]
    else:
        args = ["--all-files", "--show-diff-on-failure"]

    session.run("pre-commit", "run", *args)
    session.run("python", "-m", "mypy")
    if sys.version_info >= (3, 11):
        return
    session.run("python", "-m", "pylint", *locations)


@nox.session
def build(session: nox.Session) -> None:
    session.install("build", "setuptools", "twine")
    session.run("python", "-m", "build")
    dists = glob.glob("dist/*")
    session.run("twine", "check", *dists, silent=True)
