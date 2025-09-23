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

import unittest
from unittest.mock import patch

import hooked.library.git as lib


class git_tests(unittest.TestCase):
    @patch("hooked.library.git.run_cmd")
    def test_set_global_hook(self, run_cmd):
        directory = "foo"
        lib.git_set_global_hook_path(directory)
        run_cmd.assert_called_once_with(
            ["git", "config", "--global", "core.hooksPath", directory]
        )

    @patch("hooked.library.git.run_cmd")
    def test_unset_global_hook(self, run_cmd):
        lib.git_unset_global_hook_path()
        run_cmd.assert_called_once_with(
            ["git", "config", "--global", "--unset", "core.hooksPath"]
        )

    @patch("hooked.library.git.run_cmd")
    def test_set_template_dir(self, run_cmd):
        directory = "bar"
        lib.git_set_template_dir(directory)
        run_cmd.assert_called_once_with(
            ["git", "config", "--global", "init.templateDir", directory]
        )

    @patch("hooked.library.git.run_cmd")
    def test_unset_template_dir(self, run_cmd):
        lib.git_unset_template_dir()
        run_cmd.assert_called_once_with(
            ["git", "config", "--global", "--unset", "init.templateDir"]
        )

    @patch("hooked.library.git.run_cmd")
    def test_get_tags(self, run_cmd):
        sha = "988881adc9fc3655077dc2d4d757d480b5ea0e11"
        tag = "v1.2.3"
        run_cmd.return_value.stdout = (
            "8a6c0e3aeef498cb1ed8308df5c0269eb720e5c4\tThis line should not interfere\n"
            + f"{sha}\trefs/tags/{tag}\n"
            + "77bcd416f8bbe8bf359f45048f51360003fe8851\tAlso this line should be fine!\n"
        )

        url = "git+https://git.example.com/hooked.git"
        tags = lib.git_get_tags(url=url)

        run_cmd.assert_called_once_with(
            ["git", "ls-remote", "--tags", "--refs", url[4:]]
        )
        self.assertEqual(tags, [(tag, sha)])

    @patch("hooked.library.git.run_cmd")
    def test_get_last_branch_commit(self, run_cmd):
        sha = "52a9e0f1d18d7084993cc6e4bf01bb24a1c609ea"
        branch = "main"
        run_cmd.return_value.stdout = (
            "f4d1f7c42304573858383f39582c67aff7d3b3cd\tThis line should not interfere\n"
            + f"{sha}\trefs/heads/{branch}\n"
            + "38435af72807f13f345da0e85e4257a6374e3bc9\tAlso this line should be fine!\n"
        )

        url = "git+https://git.example.com/hooked.git"
        ref = lib.git_get_last_branch_commit(url=url, branch=branch)

        run_cmd.assert_called_once_with(
            ["git", "ls-remote", "--heads", url[4:], branch]
        )
        self.assertEqual(ref, sha)
