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

import logging

import pytest


class TestLogger:
    @pytest.fixture(autouse=True)
    def _reset_logger_level(self):
        from hooked.library import logger as logger_mod

        original = logger_mod.logger.level
        try:
            yield
        finally:
            logger_mod.logger.setLevel(original)

    def test_set_log_level_known_names_case_insensitive(self):
        from hooked.library.logger import logger, set_log_level

        set_log_level("info")
        assert logger.getEffectiveLevel() == logging.INFO
        set_log_level("DeBuG")
        assert logger.getEffectiveLevel() == logging.DEBUG

    def test_unknown_level_falls_back_to_warning(self, caplog):
        from hooked.library.logger import logger, set_log_level

        with caplog.at_level(logging.WARNING, logger="hooked"):
            set_log_level("nope")
        assert logger.getEffectiveLevel() == logging.WARNING
        assert any(rec.levelno == logging.WARNING for rec in caplog.records)
