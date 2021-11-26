import os

from pytest_test_utils import TmpDir


def test_is_tmp_dir(tmp_dir: TmpDir) -> None:
    assert isinstance(tmp_dir, TmpDir)


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
