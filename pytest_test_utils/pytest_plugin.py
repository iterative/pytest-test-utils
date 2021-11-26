from pathlib import Path
from typing import Iterator

import pytest

from .tmp_dir import TmpDir


@pytest.fixture
def tmp_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TmpDir]:
    tmp = TmpDir(tmp_path)
    monkeypatch.chdir(tmp)
    yield tmp
