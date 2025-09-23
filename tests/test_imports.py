#  Copyright 2025 T-Systems International GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#  Copyright 2025 T-Systems International GmbH
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import importlib
import pkgutil
import sys
from pathlib import Path

import pytest

EXCLUDE_DIRS = {"tests", "build", "dist", ".venv", "venv", "__pycache__"}
EXCLUDE_MODULE_SUBSTR = (
    ".tests.",
    ".test.",
    ".contrib.",
    ".examples.",
    ".benchmark.",
    ".bench.",
)


def _project_root() -> Path:
    # Assuming this file lives in '<root>/tests'
    return Path(__file__).resolve().parent.parent


def _search_roots() -> list[Path]:
    root = _project_root()
    src = root / "src"
    return [src] if src.is_dir() else [root]


def _ensure_sys_path(paths: list[Path]) -> None:
    for p in paths:
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)


def _discover_top_level_packages() -> list[Path]:
    packages = []
    for base in _search_roots():
        for entry in base.iterdir():
            if (
                entry.is_dir()
                and (entry / "__init__.py").exists()
                and entry.name not in EXCLUDE_DIRS
                and not entry.name.startswith(".")
            ):
                packages.append(entry)
    return packages


def _iter_all_module_names() -> list[str]:
    """
    Return fully qualified module names for all modules under discovered packages.
    Excludes obvious test/example/bench modules.
    """
    _ensure_sys_path(_search_roots())
    module_names: set[str] = set()

    for pkg_path in _discover_top_level_packages():
        pkg_name = pkg_path.name
        # Include the package itself
        module_names.add(pkg_name)

        for mod in pkgutil.walk_packages([str(pkg_path)], prefix=f"{pkg_name}."):
            name = mod.name
            if any(substr in name for substr in EXCLUDE_MODULE_SUBSTR):
                continue
            module_names.add(name)

    return sorted(module_names)


ALL_MODULES = _iter_all_module_names()


@pytest.mark.parametrize("modname", ALL_MODULES, ids=lambda n: n)
def test_imports_smoke(modname: str) -> None:
    """
    Import every module once. This lifts coverage on module-level code and
    surfaces import-time errors or missing optional deps.
    """
    try:
        importlib.import_module(modname)
    except ImportError as e:
        pytest.skip(f"Skipped {modname} due to optional dependency: {e}")
