from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Type

import pytest

from . import TempDirFactory, TmpDir, matchers

if TYPE_CHECKING:
    from pytest import MonkeyPatch, TempPathFactory


@pytest.fixture(scope="session")
def tmp_dir_factory(tmp_path_factory: "TempPathFactory") -> TempDirFactory:
    return TempDirFactory(tmp_path_factory)


@pytest.fixture
def tmp_dir(tmp_path: Path, monkeypatch: "MonkeyPatch") -> Iterator[TmpDir]:
    tmp = TmpDir(tmp_path)
    monkeypatch.chdir(tmp_path)
    yield tmp


@pytest.fixture(name="matcher")
def matcher_fixture() -> Type["matchers.Matcher"]:
    return matchers.Matcher


@pytest.fixture(name="M")
def m_fixture() -> Type["matchers.Matcher"]:
    return matchers.Matcher
