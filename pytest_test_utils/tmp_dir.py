import os
from contextlib import contextmanager
from pathlib import Path


class TmpDir(type(Path())):  # type: ignore
    def gen(self, struct, text=""):
        if isinstance(struct, (str, bytes, os.PathLike)):
            struct = {struct: text}
        for name, contents in struct.items():
            path = self / os.fsdecode(name)

            if isinstance(contents, dict):
                if not contents:
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.gen(contents)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(contents, bytes):
                    path.write_bytes(contents)
                else:
                    path.write_text(contents, encoding="utf-8")

        return list(struct.keys())

    @contextmanager
    def chdir(self):
        old = os.getcwd()
        try:
            os.chdir(self)
            yield
        finally:
            os.chdir(old)
