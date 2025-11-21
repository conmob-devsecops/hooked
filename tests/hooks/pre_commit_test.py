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

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from hooked.hooks import pre_commit as lib
from hooked.library import files


class PreCommitHookTests(unittest.TestCase):
    @patch("hooked.hooks.pre_commit._do_autoupdate")
    @patch("hooked.hooks.pre_commit._check_autoupdate")
    @patch("hooked.hooks.pre_commit._flag_is_set")
    @patch("hooked.hooks.pre_commit._run_internal_precommit")
    @patch("hooked.hooks.pre_commit._normalize_cwd")
    @patch("hooked.hooks.pre_commit.git")
    @patch("hooked.hooks.pre_commit.pre_commit")
    def test_run(
        self,
        pre_commit,
        git,
        _normalize_cwd,
        _run_internal_precommit,
        _flag_is_set,
        _check_autoupdate,
        _do_autoupdate,
    ):
        cwd = "/tmp"
        _normalize_cwd.return_value = cwd
        _check_autoupdate.return_value = False
        _flag_is_set.return_value = True
        pre_commit.is_pre_commit_available.return_value = True
        pre_commit.is_pre_commit_installed.return_value = True
        git.git_has_hook_installed.return_value = False
        git.git_run_hook.return_value = False

        # basic run
        lib.run(cwd=cwd)
        _normalize_cwd.assert_called_once_with(cwd=cwd)
        _check_autoupdate.assert_called_once()
        _flag_is_set.assert_called_once_with("HOOKED_SKIP")
        pre_commit.is_pre_commit_available.assert_called_once_with(repo=cwd)
        pre_commit.is_pre_commit_installed.assert_called_once_with(repo=cwd)
        git.git_has_hook_installed.assert_called_once_with(repo=cwd, hook="pre-commit")

        # with auto update
        _check_autoupdate.return_value = True
        lib.run(cwd=cwd)
        _do_autoupdate.assert_called_once()

        # (un-)skip hooked
        _flag_is_set.return_value = False
        lib.run(cwd=cwd)
        _run_internal_precommit.assert_called_once_with(cwd=cwd)

        # install pre-commit
        pre_commit.is_pre_commit_installed.return_value = False
        lib.run(cwd=cwd)
        pre_commit.pre_commit_install.assert_called_once_with(repo=cwd)

        # run git hook
        git.git_has_hook_installed.return_value = True
        lib.run(cwd=cwd)
        git.git_run_hook.assert_called_once_with(repo=cwd, hook="pre-commit")

    @patch("os.getenv")
    def test_env_flags(self, getenv):
        var = "HOOKED_SKIP"

        getenv.return_value = "1"
        self.assertTrue(lib._flag_is_set(env_var=var))

        getenv.return_value = "tRue"
        self.assertTrue(lib._flag_is_set(env_var=var))

        getenv.return_value = "yEs"
        self.assertTrue(lib._flag_is_set(env_var=var))

        getenv.return_value = "0"
        self.assertFalse(lib._flag_is_set(env_var=var))

        getenv.return_value = "do3s_NoT_w0rk!"
        self.assertFalse(lib._flag_is_set(env_var=var))

    @patch("os.environ.copy")
    @patch("hooked.hooks.pre_commit.pre_commit")
    def test_run_internal_precommit(self, pre_commit, copy):
        cwd = "/path/to/repo"
        config = os.path.join(files.get_config_dir(), ".pre-commit-config.yaml")
        empty_env = {}
        target_env = {
            "GITLEAKS_CONFIG": os.path.join(files.get_config_dir(), ".gitleaks.toml")
        }
        copy.return_value = empty_env

        lib._run_internal_precommit(cwd=cwd)
        pre_commit.pre_commit_run.assert_called_once_with(
            config=config, env=target_env, cwd=cwd
        )
