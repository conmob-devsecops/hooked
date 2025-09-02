#!/usr/bin/env bash
# Copyright (C) 2025 T-Systems International GmbH.
#
# You can find the compulsory statement on:
# https://www.t-systems.com/de/en/compulsory-statement
#
# All rights, including licensing, inspection, modification and sharing of
# software and source code, reserved.

set -e

mkdir -p ~/.config
mv ~/.config/git{,.bak}
git clone https://github.com/conmob-devops/git-hooks ~/.config/git
git config --global core.hooksPath ~/.config/git/core/hooks

# install pre-commit if needed
if ! command -v pre-commit &>/dev/null; then
  if command -v brew &>/dev/null; then
    brew install pre-commit
  elif command -v pip &>/dev/null; then
    pip install pre-commit
  fi
fi
