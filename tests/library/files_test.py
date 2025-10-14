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
from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import call, patch

import hooked.library.files as lib


class TestFiles(unittest.TestCase):
    home = os.path.expanduser("~")

    def test_get_base_dir(self):
        self.assertEqual(f"{self.home}/.config/hooked", lib.get_base_dir())

    def test_get_hooks_dir(self):
        self.assertEqual(f"{self.home}/.config/hooked/git_hooks", lib.get_hooks_dir())

    def test_get_config_dir(self):
        self.assertEqual(f"{self.home}/.config/hooked/config", lib.get_config_dir())

    def test_get_template_dir(self):
        self.assertEqual(
            f"{self.home}/.config/hooked/git_template", lib.get_template_dir()
        )

    @patch("hooked.library.files.os.makedirs")
    def test_create_base_dir(self, makedirs):
        lib._create_base_dir()
        makedirs.assert_called_once_with(lib.get_base_dir(), exist_ok=True)

    @patch("hooked.library.files.os.path.exists")
    @patch("hooked.library.files.shutil.rmtree")
    def test_remove_base_dir(self, rmtree, exists):
        exists.return_value = True
        lib.remove_base_dir("foo")
        exists.assert_called_once_with("foo")
        rmtree.assert_called_once_with("foo")

    @patch("hooked.library.files.os.makedirs")
    def test_create_hooks_dir(self, makedirs):
        lib._create_hooks_dir()
        makedirs.assert_called_once_with(lib.get_hooks_dir(), exist_ok=True)

    @patch("hooked.library.files.os.makedirs")
    def test_create_temlates_dir(self, makedirs):
        lib._create_git_template_dir()
        makedirs.assert_called_once_with(lib.get_template_dir(), exist_ok=True)

    @patch("hooked.library.files.os.chmod")
    @patch("hooked.library.files.shutil.copyfile")
    def test_copy_git_hooks(self, copyfile, chmod):
        with tempfile.TemporaryDirectory() as tmp:
            lib._copy_git_hooks("hooked.data.git_hooks", tmp)
            destinations = [args[0][1] for args in copyfile.call_args_list]

            self.assertIn(f"{tmp}/post-commit", destinations)
            self.assertIn(f"{tmp}/pre-commit", destinations)

            chmod.assert_has_calls(
                [call(f"{tmp}/post-commit", 0o755), call(f"{tmp}/pre-commit", 0o755)]
            )

    @patch("hooked.library.files._copy_git_hooks")
    @patch("hooked.library.files._create_hooks_dir")
    @patch("hooked.library.files._create_git_template_dir")
    @patch("hooked.library.files._create_base_dir")
    def test_copy_hooked_files(
        self,
        _create_base_dir,
        _create_git_template_dir,
        _create_hooks_dir,
        _copy_git_hooks,
    ):
        lib.copy_hooked_files()
        _create_base_dir.assert_called_once()
        _create_git_template_dir.assert_called_once()
        _create_hooks_dir.assert_called_once()
        _copy_git_hooks.assert_has_calls(
            [
                call("hooked.data.git_hooks", lib.get_hooks_dir()),
                call("hooked.data.git_template", lib.get_template_dir()),
            ]
        )
