from typing import TYPE_CHECKING

from .tmp_dir import TmpDir

if TYPE_CHECKING:
    from pytest import TempPathFactory


class TempDirFactory:
    def __init__(self, tmp_path_factory: "TempPathFactory") -> None:
        self.tmp_path_factory: "TempPathFactory" = tmp_path_factory

    def mktemp(self, basename: str, numbered: bool = True) -> TmpDir:
        return TmpDir(self.tmp_path_factory.mktemp(basename, numbered=numbered))

    def getbasetemp(self) -> TmpDir:
        return TmpDir(self.tmp_path_factory.getbasetemp())
