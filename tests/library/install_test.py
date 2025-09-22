# Copyright 2025 T-Systems International GmbH
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from unittest.mock import patch

from hooked.library.files import get_base_dir, get_hooks_dir, get_template_dir
import hooked.library.install as lib


class InstallTests(unittest.TestCase):
    @patch("hooked.library.install.run_cmd")
    def test_get_gitleaks_version(self, run_cmd):
        run_cmd.return_value.stdout = "foo"
        self.assertEqual("foo", lib._get_gitleaks_version())
        run_cmd.assert_called_once_with(["gitleaks", "--version"])

    @patch("hooked.library.install.run_cmd")
    def test_get_git_version(self, run_cmd):
        run_cmd.return_value.stdout = "bar"
        self.assertEqual("bar", lib._get_git_version())
        run_cmd.assert_called_once_with(["git", "--version"])

    @patch("hooked.library.install.git_set_template_dir")
    @patch("hooked.library.install.git_set_global_hook_path")
    @patch("hooked.library.install.get_config_git_repo")
    @patch("hooked.library.install.copy_hooked_files")
    def test_install(
        self,
        copy_hooked_files,
        get_config_git_repo,
        git_set_global_hook_path,
        git_set_template_dir,
    ):
        rules = "git+https://git.example.com/hooked-rules.git"
        branch = "main"

        retval = lib.install(rules=rules, branch=branch)
        self.assertEqual(0, retval)

        copy_hooked_files.assert_called_once()
        get_config_git_repo.assert_called_once_with(get_base_dir(), rules, branch)
        git_set_global_hook_path.assert_called_once_with(get_hooks_dir())
        git_set_template_dir.assert_called_once_with(get_template_dir())

    @patch("hooked.library.install.git_unset_template_dir")
    @patch("hooked.library.install.git_unset_global_hook_path")
    @patch("hooked.library.install.remove_base_dir")
    def test_uninstall(
        self,
        remove_base_dir,
        git_unset_global_hook_path,
        git_unset_template_dir,
    ):
        retval = lib.uninstall()
        self.assertEqual(0, retval)

        remove_base_dir.assert_called_once_with(get_base_dir())
        git_unset_global_hook_path.assert_called_once()
        git_unset_template_dir.assert_called_once()

    @patch("hooked.library.install._check_git")
    @patch("hooked.library.install._check_gitleaks")
    def test_check_pre_requisities(self, _check_gitleaks, _check_git):
        retval = lib.check_pre_requisites()
        self.assertEqual(0, retval)
        _check_gitleaks.assert_called_once()
        _check_git.assert_called_once()

    @patch("hooked.library.install._check_git")
    @patch("hooked.library.install._check_gitleaks")
    def test_check_pre_requisities_error1(self, _check_gitleaks, _check_git):
        _check_gitleaks.side_effect = RuntimeError()
        retval = lib.check_pre_requisites()
        self.assertEqual(1, retval)
        _check_gitleaks.assert_called_once()
        _check_git.assert_not_called()

    @patch("hooked.library.install._check_git")
    @patch("hooked.library.install._check_gitleaks")
    def test_check_pre_requisities_error2(self, _check_gitleaks, _check_git):
        _check_git.side_effect = RuntimeError()
        retval = lib.check_pre_requisites()
        self.assertEqual(1, retval)
        _check_gitleaks.assert_called_once()
        _check_git.assert_called_once()
