import os
from pathlib import Path

import pytest

from pytest_test_utils import ANY, TmpDir
from pytest_test_utils.tmp_dir_factory import TempDirFactory


def test_any() -> None:
    assert ANY(str) == "5"
    assert ANY(str) != 5

    with pytest.raises(AssertionError):
        assert ANY(int) != 5
    assert ANY(int) == 5
    assert repr(ANY(int)) == "ANY(int)"


def test_is_tmp_dir(tmp_dir: TmpDir) -> None:
    assert isinstance(tmp_dir, TmpDir)


def test_tmp_dir_fixture_changes_dir(tmp_path: Path, tmp_dir: TmpDir) -> None:
    assert Path.cwd() == tmp_path == tmp_dir


def test_gen_str(tmp_dir: TmpDir) -> None:
    assert tmp_dir.gen("foo", "lorem ipsum") == ["foo"]
    assert (tmp_dir / "foo").read_text() == "lorem ipsum"


def test_gen_bytes(tmp_dir: TmpDir) -> None:
    assert tmp_dir.gen(b"foo", "lorem ipsum") == [b"foo"]
    assert (tmp_dir / os.fsdecode(b"foo")).read_bytes() == b"lorem ipsum"


def test_gen_dict_str(tmp_dir: TmpDir) -> None:
    assert tmp_dir.gen({"file": "lorem", "dir": {"file": "ipsum"}}) == [
        "file",
        "dir",
    ]
    assert (tmp_dir / "file").read_text() == "lorem"
    assert (tmp_dir / "dir").is_dir()
    assert (tmp_dir / "dir" / "file").read_text() == "ipsum"


def test_gen_dict_bytes(tmp_dir: TmpDir) -> None:
    assert tmp_dir.gen({b"file": b"lorem", b"dir": {b"file": b"ipsum"}}) == [
        b"file",
        b"dir",
    ]
    assert (tmp_dir / os.fsdecode("file")).read_bytes() == b"lorem"
    assert (tmp_dir / os.fsdecode("dir")).is_dir()
    assert (
        tmp_dir / os.fsdecode("dir") / os.fsdecode("file")
    ).read_bytes() == b"ipsum"


def test_chdir(tmp_path: Path, tmp_dir: TmpDir) -> None:
    subdir = tmp_dir / "dir"
    subdir.mkdir()
    with subdir.chdir():
        assert Path.cwd() == subdir
        assert Path.cwd() == tmp_path / "dir"
        assert Path.cwd() == tmp_dir / "dir"


def test_cat(tmp_dir: TmpDir) -> None:
    tmp_dir.gen({"dir": {"file": "lorem ipsum"}})

    assert tmp_dir.cat() == {"dir": {"file": "lorem ipsum"}}
    assert (tmp_dir / "dir").cat() == {"file": "lorem ipsum"}
    assert (tmp_dir / "dir" / "file").cat() == "lorem ipsum"


def test_tmp_dir_factory(tmp_dir_factory: TempDirFactory) -> None:
    tmp_dir = tmp_dir_factory.mktemp("test-dir")
    assert isinstance(tmp_dir, TmpDir)
    assert isinstance(tmp_dir, os.PathLike)
    assert isinstance(tmp_dir, Path)
    assert "test-dir0" in tmp_dir.name

    tmp_dir.gen({"foo": "foo"})
    assert tmp_dir.cat() == {"foo": "foo"}

    assert "test-dir1" in tmp_dir_factory.mktemp("test-dir").name
