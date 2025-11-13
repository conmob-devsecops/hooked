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
from unittest.mock import call, patch

import hooked.library.config as lib
from hooked.library.cmd_util import CommandError, CommandResult


class TestConfig(unittest.TestCase):
    @patch("hooked.library.config.run_cmd")
    def test_get_config(self, run_cmd):
        base_dir = "~/.config/hooked"
        repo = "https://git.example.com/hooked.git"
        branch = "main"
        lib.install_config(base_dir=base_dir, repo=repo, branch=branch)

        run_cmd.assert_has_calls(
            [
                call(["git", "clone", repo, "~/.config/hooked/config"]),
                call(["git", "-C", "~/.config/hooked/config", "checkout", branch]),
            ]
        )

    @patch("hooked.library.config.run_cmd")
    def test_install_config_error(self, run_cmd):
        run_cmd.side_effect = CommandError(CommandResult([], 1, "", ""))

        base_dir = "~/.config/hooked"
        repo = "https://git.example.com/hooked.git"
        branch = "main"

        with self.assertRaises(CommandError):
            lib.install_config(base_dir=base_dir, repo=repo, branch=branch)

    @patch("os.path.isdir")
    @patch("hooked.library.config.run_cmd")
    def test_update_config(self, run_cmd, isdir):
        isdir.return_value = True
        base_dir = "~/.config/hooked"
        lib.update_config(base_dir, force=False)

        run_cmd.assert_has_calls(
            [
                call(
                    [
                        "git",
                        "-C",
                        f"{base_dir}/config",
                        "fetch",
                        "--prune",
                        "--tags",
                        "origin",
                    ]
                ),
                call(
                    [
                        "git",
                        "-C",
                        f"{base_dir}/config",
                        "-c",
                        "rebase.autoStash=true",
                        "pull",
                        "--no-rebase",
                        "--no-edit",
                        "--strategy-option",
                        "ours",
                    ]
                ),
            ]
        )

    @patch("os.path.isdir")
    @patch("hooked.library.config.run_cmd")
    def test_update_config_force(self, run_cmd, isdir):
        isdir.return_value = True
        base_dir = "~/.config/hooked"
        lib.update_config(base_dir=base_dir, force=True)

        run_cmd.assert_has_calls(
            [
                call(
                    [
                        "git",
                        "-C",
                        f"{base_dir}/config",
                        "fetch",
                        "--prune",
                        "--tags",
                        "origin",
                    ]
                ),
                call(
                    [
                        "git",
                        "-C",
                        f"{base_dir}/config",
                        "reset",
                        "--hard",
                        "origin/HEAD",
                    ]
                ),
            ]
        )
