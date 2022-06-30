import os
from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
from typing import TYPE_CHECKING, Type
from unittest.mock import MagicMock

import pytest

from pytest_test_utils import TmpDir, matchers
from pytest_test_utils.matchers import Matcher
from pytest_test_utils.tmp_dir_factory import TempDirFactory
from pytest_test_utils.waiters import TimedOutError, wait_until

if TYPE_CHECKING:
    from pytest import TempPathFactory

# pylint: disable=redefined-outer-name


def test_is_tmp_dir(tmp_dir: TmpDir) -> None:
    assert isinstance(tmp_dir, TmpDir)


def test_tmp_dir_name(tmp_dir: TmpDir) -> None:
    assert tmp_dir.name == "test_tmp_dir_name0"


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


def test_gen_dict_empty(tmp_dir: TmpDir) -> None:
    assert tmp_dir.gen({"dir": {}}) == ["dir"]
    assert (tmp_dir / "dir").is_dir()
    assert not list((tmp_dir / "dir").iterdir())


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


def test_tmp_dir_factory(
    tmp_path_factory: "TempPathFactory", tmp_dir_factory: TempDirFactory
) -> None:
    assert isinstance(tmp_dir_factory, TempDirFactory)
    tmp_dir = tmp_dir_factory.mktemp("test-dir")
    assert isinstance(tmp_dir, TmpDir)
    assert isinstance(tmp_dir, os.PathLike)
    assert isinstance(tmp_dir, Path)
    assert "test-dir0" in tmp_dir.name

    tmp_dir.gen({"foo": "foo"})
    assert tmp_dir.cat() == {"foo": "foo"}

    assert "test-dir1" in tmp_dir_factory.mktemp("test-dir").name
    assert isinstance(tmp_dir_factory.getbasetemp(), TmpDir)
    assert tmp_dir_factory.getbasetemp() == tmp_path_factory.getbasetemp()


def test_matcher_repr(matcher: Type[Matcher]) -> None:
    assert repr(matcher.any) == "any"
    assert repr(matcher.attrs(foo="foo")) == "attrs(foo='foo')"
    assert repr(matcher.any_of(3, 4)) == "any_of(3, 4)"
    assert (
        repr(matcher.dict(foo="foo", **{"bar": "bar"}))
        == "dict(foo='foo', bar='bar')"
    )
    assert repr(matcher.instance_of(str)) == "instance_of(str)"
    assert (
        repr(matcher.instance_of((str, bytes))) == "instance_of((str, bytes))"
    )
    assert repr(matcher.unordered("foo", "bar")) == "unordered('foo', 'bar')"
    assert (
        repr(matcher.re(r"^plots\.csv-\w+$")) == "regex(r'^plots\\.csv-\\w+$')"
    )


def test_matcher_dict(matcher: Type[Matcher]) -> None:
    # pytest needs len() to be there when there is no explanation
    assert len(matcher.dict({"a": 1, "b": 2})) == 2

    actual = {"base_url": "url", "verify": "bundle", "timeout": 10}
    assert actual == matcher.dict(verify="bundle", timeout=10)
    assert actual == matcher.dict(actual, verify="bundle")
    assert actual != matcher.dict(verify="bundle.pem")


def test_matcher_regex(matcher: Type[Matcher]) -> None:
    assert matcher.regex(r"^500 Internal") == "500 Internal Error"
    assert matcher.regex("^500 Internal") != "200 OK"


def test_matcher_attrs(matcher: Type[Matcher]) -> None:
    obj = SimpleNamespace(foo="foo", bar="bar")
    assert obj == matcher.attrs(foo="foo")
    assert obj != matcher.attrs(bar="b")


def test_matcher_attrs_nested(matcher: Type[Matcher]) -> None:
    obj = SimpleNamespace(
        nested=SimpleNamespace(foo="foo", bar="bar"), foobar="bar"
    )
    assert obj == matcher.attrs(nested=matcher.attrs(foo="foo"))


def test_matcher_any(matcher: Type[Matcher]) -> None:
    assert matcher.any == 5
    assert bool(matcher.any)


def test_matcher_instance_of(matcher: Type[Matcher]) -> None:
    assert matcher.instance_of(str) == "5"
    assert matcher.instance_of(str) != 5

    with pytest.raises(AssertionError):
        assert matcher.instance_of(int) != 5
    assert matcher.instance_of(int) == 5
    assert repr(matcher.instance_of(int)) == "instance_of(int)"


def test_matcher_instance_of_tuple(matcher: Type[Matcher]) -> None:
    assert matcher.instance_of((int, str)) == 5
    assert matcher.instance_of((int, str)) == "5"
    assert matcher.instance_of((int, str)) != 5.0


def test_matcher_unordered(matcher: Type[Matcher]) -> None:
    lst = ["foo", "foobar", "bar"]
    assert lst == matcher.unordered("foo", "bar", "foobar")
    assert lst != matcher.unordered("foo", "bar")


def test_matcher_any_of(matcher: Type[Matcher]) -> None:
    lst1 = ["foo", "foobar"]
    lst2 = ["bar", "foobar"]
    lst3 = ["foo", "bar", "foobar"]

    assert matcher.any_of("foo", "bar") == "foo"
    assert matcher.any_of("foo", "bar") == "bar"
    assert matcher.any_of("foo", "bar") != "foobar"
    assert matcher.any_of("foo", "bar") in lst1
    assert matcher.any_of("foo", "bar") in lst2
    assert matcher.any_of("foo", "bar") in lst3
    assert matcher.any_of("foo", "bar") not in []
    assert matcher.any_of("foo", "bar") not in ["foobar"]


def test_approx_datetime_repr(matcher: Type[Matcher]) -> None:
    obj = matcher.approx(datetime(2021, 11, 29))
    assert repr(obj) == (
        "approx_datetime(datetime.datetime(2021, 11, 29, 0, 0) "
        "± datetime.timedelta(seconds=1))"
    )


def test_approx_datetime(matcher: Type[Matcher]) -> None:
    assert matcher.approx(datetime.now()) == datetime.now()
    with pytest.raises(AssertionError):
        expected = datetime.now() - timedelta(seconds=10)
        assert matcher.approx(expected) == datetime.now()


def test_approx_should_fallback_to_pytest(matcher: Type[Matcher]) -> None:
    assert matcher.approx(3.0 + 1e-6) == 3


def test_matcher(matcher: Type[Matcher]) -> None:
    experiments = {
        "b05eec": {
            "baseline": {
                "data": {
                    "timestamp": datetime(2021, 8, 2, 16, 48, 14),
                    "params": {
                        "params.yaml": {
                            "data": {
                                "featurize": {
                                    "max_features": 3000,
                                    "ngrams": 1,
                                },
                                "parent": 20170428,
                                "train": {
                                    "n_est": 100,
                                    "min_split": 2,
                                },
                            }
                        }
                    },
                    "name": "master",
                }
            }
        }
    }

    assert experiments == {
        "b05eec": {
            "baseline": {
                "data": matcher.dict(
                    timestamp=matcher.approx(datetime(2021, 8, 2, 16, 48, 15)),
                    params={
                        "params.yaml": matcher.dict(
                            data=matcher.dict(
                                featurize=matcher.any,
                                parent=20170428,
                                train=matcher.dict(n_est=100),
                            )
                        ),
                    },
                    name=matcher.re(r"master"),
                )
            }
        }
    }


def test_matcher_as_attrs(matcher: Type[Matcher]) -> None:
    assert issubclass(matcher, matchers.attrs)
    obj = SimpleNamespace(foo="foo", bar="bar")
    assert obj == matcher(foo="foo")
    assert obj != matcher(bar="b")


def test_matcher_alias(  # pylint: disable=invalid-name
    M: Type[Matcher], matcher: Type[Matcher]
) -> None:
    assert matcher is M is Matcher


def test_wait_until() -> None:
    pred = MagicMock(side_effect=[False, False, True])

    start = perf_counter()
    assert wait_until(pred, 0.01, pause=0.0001)
    assert perf_counter() == pytest.approx(start + 0.0002, rel=1e-3)
    assert len(pred.call_args_list) == 3


def test_wait_until_raises_timedouterror() -> None:
    pred = MagicMock(return_value=False)

    start = perf_counter()

    with pytest.raises(TimedOutError):
        wait_until(pred, 0.01, pause=0.0001)

    assert perf_counter() == pytest.approx(start + 0.01, rel=1e-3)
    assert len(pred.call_args_list) > 1
