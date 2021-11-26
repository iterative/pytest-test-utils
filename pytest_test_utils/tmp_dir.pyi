import os
from pathlib import Path
from typing import Any, ContextManager, Dict, List, TypeVar, Union, overload

T = TypeVar("T", str, bytes)
Text = Union[str, bytes]
AnyPath = Union[T, os.PathLike[T]]
AnyStruct = Dict[AnyPath[T], Union[Text, Dict[AnyPath[T], Any]]]
StrStruct = AnyStruct[str]
BytesStruct = AnyStruct[bytes]

CatStruct = Union[str, Dict[str, Union[str, Dict[str, Any]]]]

class TmpDir(Path):
    @overload
    def gen(self, struct: AnyPath[T], text: Text = "") -> List[T]: ...
    @overload
    def gen(self, struct: BytesStruct, text: Text = "") -> List[bytes]: ...
    @overload
    def gen(self, struct: StrStruct, text: Text = "") -> List[str]: ...
    def chdir(self) -> ContextManager[None]: ...
    def cat(self) -> CatStruct: ...
