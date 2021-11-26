from pathlib import Path
from typing import Iterator

import pytest
from pytest import TempPathFactory

from . import TempDirFactory, TmpDir


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
