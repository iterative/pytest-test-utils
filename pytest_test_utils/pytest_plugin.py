from pathlib import Path
from typing import Iterator, Type

import pytest
from pytest import TempPathFactory

from . import TempDirFactory, TmpDir, matchers


@pytest.fixture(scope="session")
def tmp_dir_factory(tmp_path_factory: TempPathFactory) -> TempDirFactory:
    return TempDirFactory(tmp_path_factory)


@pytest.fixture
def tmp_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TmpDir]:
    tmp = TmpDir(tmp_path)
    monkeypatch.chdir(tmp_path)
    yield tmp


@pytest.fixture(name="matcher")
def matcher_fixture() -> Type["matchers.Matcher"]:
    return matchers.Matcher


@pytest.fixture(name="M")
def m_fixture() -> Type["matchers.Matcher"]:
    return matchers.Matcher
