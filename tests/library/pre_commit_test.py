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

import hooked.library.pre_commit as lib
from hooked.library.cmd import CommandError, CommandResult


class PreCommitTests(unittest.TestCase):
    @patch("hooked.library.pre_commit.install")
    @patch("hooked.library.pre_commit.run_cmd")
    def test_pre_commit_install(self, run_cmd, install):
        repo = "/path/to/repo"
        lib.pre_commit_install(repo=repo)

        install.disable.assert_called_once()
        run_cmd.assert_called_once_with(["pre-commit", "install"], cwd=repo)
        install.enable.assert_called_once()

    @patch("hooked.library.pre_commit.install")
    @patch("hooked.library.pre_commit.run_cmd")
    def test_pre_commit_install_failed(self, run_cmd, install):
        repo = "/path/to/repo"
        run_cmd.side_effect = CommandError(
            CommandResult(
                cmd=[""],
                returncode=1,
                stdout=None,
                stderr="Cowardly refusing to install hooks with `core.hooksPath` set.",
            )
        )

        with self.assertRaises(CommandError):
            lib.pre_commit_install(repo=repo)

        install.disable.assert_called_once()
        run_cmd.assert_called_once_with(["pre-commit", "install"], cwd=repo)
        install.enable.assert_called_once()

    @patch("hooked.library.pre_commit.run_stream")
    def test_pre_commit_run(self, run_stream):
        config = "/path/to/.pre-commit-config.yaml"
        env = {"foo": "bar"}
        cwd = "/root"

        lib.pre_commit_run(config=config, env=env, cwd=cwd)

        run_stream.assert_called_once_with(
            ["pre-commit", "run", "--config", config], env=env, cwd=cwd
        )

    @patch("hooked.library.pre_commit.run_stream")
    def git_pre_commit_run_error(self, run_stream):
        config = "/path/to/.pre-commit-config.yaml"
        env = {"foo": "bar"}
        cwd = "/root"

        run_stream.side_effect = CommandError(
            CommandResult(
                cmd=[""],
                returncode=127,
                stdout=None,
                stderr="oh oh could not run pre-commit",
            )
        )

        with self.assertRaises(CommandError):
            lib.pre_commit_run(config=config, env=env, cwd=cwd)

    @patch("hooked.library.pre_commit.run_cmd")
    def test_pre_commit_autoupdate(self, run_cmd):
        repo = "/path/to/repo"
        lib.pre_commit_autoupdate(repo=repo)

        run_cmd.assert_called_once_with(["pre-commit", "autoupdate"], cwd=repo)

    @patch("hooked.library.pre_commit.run_cmd")
    def test_pre_commit_autoupdate_failed(self, run_cmd):
        repo = "/path/to/repo"
        run_cmd.side_effect = CommandError(
            CommandResult(
                cmd=[""],
                returncode=1,
                stdout=None,
                stderr="Cowardly refusing to install hooks with `core.hooksPath` set.",
            )
        )

        with self.assertRaises(CommandError):
            lib.pre_commit_autoupdate(repo=repo)
