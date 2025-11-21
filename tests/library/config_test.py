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

import unittest
from unittest.mock import patch

import hooked.library.config as lib
from hooked.library import files


class TestConfig(unittest.TestCase):
    @patch("os.path.isdir")
    @patch("hooked.library.files.remove_config_dir")
    @patch("hooked.library.config.git")
    def test_install_config_replace(self, git, remove_config_dir, isdir):
        isdir.return_value = True
        config_dir = files.get_config_dir()
        repo = "https://git.example.com/hooked.git"
        branch = "main"

        lib.install_config(repo=repo, branch=branch)

        isdir.assert_called_once_with(config_dir)
        remove_config_dir.assert_called_once()

        git.git_clone_repo.assert_called_once_with(repo=repo, dest=config_dir)
        git.git_checkout_branch.assert_called_once_with(repo=config_dir, branch=branch)

    @patch("os.path.isdir")
    @patch("hooked.library.config.git")
    def test_update_config(
        self,
        git,
        isdir,
    ):
        isdir.return_value = True
        git.is_git_repo.return_value = True
        config_dir = files.get_config_dir()

        lib.update_config(force=False)
        git.git_fetch_origin.assert_called_once_with(repo=config_dir)
        git.git_try_merge.assert_called_once_with(repo=config_dir)
        self.assertFalse(git.git_reset_hard_to_origin.called)

        lib.update_config(force=True)
        git.git_reset_hard_to_origin.assert_called_once_with(repo=config_dir)

    @patch("os.path.isdir")
    @patch("hooked.library.config.git")
    def test_update_config_not_a_dir(self, git, isdir):
        isdir.return_value = False

        with self.assertRaises(FileNotFoundError):
            lib.update_config()

        self.assertFalse(git.is_git_repo.called)
        self.assertFalse(git.git_fetch_origin.called)
        self.assertFalse(git.git_reset_hard_to_origin.called)
        self.assertFalse(git.git_try_merge.called)

    @patch("os.path.isdir")
    @patch("hooked.library.config.git")
    def test_update_config_not_a_repo(self, git, isdir):
        isdir.return_value = True
        git.is_git_repo.return_value = False

        with self.assertRaises(RuntimeError):
            lib.update_config()

        self.assertFalse(git.git_fetch_origin.called)
        self.assertFalse(git.git_reset_hard_to_origin.called)
        self.assertFalse(git.git_try_merge.called)
