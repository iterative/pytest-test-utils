"""Automation using nox.
"""
import glob

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = "lint", "tests", "tests-pytest5"
locations = "pytest_test_utils", "tests.py"


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def tests(session: nox.Session) -> None:
    session.install(".[tests]")
    # `pytest --cov` will start coverage after pytest
    # so we need to use `coverage`.
    session.run("coverage", "run", "-m", "pytest")
    session.run("coverage", "report", "--show-missing", "--skip-covered")


@nox.session(python=["3.7"], name="tests-pytest5")
def tests_pytest5(session: nox.Session) -> None:
    session.install(".[tests]")
    session.install("pytest==5.0.0")
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
    session.run("python", "-m", "pylint", *locations)


@nox.session
def build(session: nox.Session) -> None:
    session.install("build", "setuptools", "twine")
    session.run("python", "-m", "build")
    dists = glob.glob("dist/*")
    session.run("twine", "check", *dists, silent=True)
