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

import importlib.metadata as md
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime

from packaging.version import InvalidVersion, Version

from hooked import __pkg_name__

from .cmd_util import run_cmd
from .files import get_base_dir
from .git import git_get_last_branch_commit, git_get_tags
from .logger import logger

SEMVER_TAG_RE = re.compile(r"^v?\d+\.\d+\.\d+([.-].+)?$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)


# values from direct_url.json
@dataclass
class InstallInfo:
    """Represents installation info from direct_url.json."""

    url: str | None = None
    requested_revision: str | None = None
    commit: str | None = None
    is_vcs: bool = False
    is_editable: bool = False


def _run_pip(*args: str) -> int:
    """Wrapper around pip subprocess call."""
    logger.debug("Running pip command: %s", args)
    return run_cmd([sys.executable, "-m", "pip", *args]).returncode


# thank god for PEP 610
# ref: https://peps.python.org/pep-0610/
def get_install_info() -> InstallInfo:
    """
    Reads installation info from direct_url.json.
    """
    dist = md.distribution(__pkg_name__)
    install_info = InstallInfo()
    try:
        raw = dist.read_text("direct_url.json")
        info = json.loads(raw)
        install_info.url = info.get("url")
        vcs = info.get("vcs_info", {})
        dir_info = info.get("dir_info", {})
        if dir_info:
            install_info.editable = dir_info.get("editable", False)
        if install_info.url and vcs and vcs.get("vcs") == "git":
            install_info.is_vcs = True
            install_info.requested_revision = vcs.get("requested_revision")
            install_info.commit = vcs.get("commit_id")
    except TypeError:
        raise RuntimeError(
            "Could not find installation metadata; was hooked installed via Git?"
        )

    logger.debug("Installation info: %s", install_info)
    return install_info


def get_latest_release(tags: list[tuple[str, str]]) -> str | None:
    """
    Pick the highest semver tag.

    Tuple elements are (tag, sha).
    """
    semver_tags: list[tuple[Version, str]] = []

    # filter all semver tags
    for tag, _sha in tags:
        if not SEMVER_TAG_RE.match(tag):
            continue
        try:
            semver = Version(tag)
        except InvalidVersion:
            continue
        semver_tags.append((semver, tag))
    if not semver_tags:
        return None
    semver_tags.sort(key=lambda x: x[0])

    # returns first entry of sorted list, and thus the highest version
    # tuple element [1] is the original tag string
    logger.debug("Latest semver tag: %s", semver_tags[0])
    return semver_tags[-1][1]


def get_sha_for_tag(tags: list[tuple[str, str]], tag: str) -> str | None:
    """Returns sha for given tag, or None if not found."""
    for t, sha in tags:
        if t == tag:
            logger.debug("Found sha: %s", sha)
            return sha
    logger.warning("Could not find sha for tag: %s", tag)
    return None


def _is_semver_tag(ref: str) -> bool:
    """Checks if given ref is a semver tag."""
    return bool(ref and SEMVER_TAG_RE.match(ref))


def _is_sha(ref: str) -> bool:
    """Checks if given ref is an SHA."""
    return bool(ref and SHA_RE.match(ref))


def get_url_ref(url: str, ref: str) -> str:
    """Returns pip install spec for given url and ref."""
    # pip expects 'git+<url>@<ref>#egg=<name>'
    prefix = "git+" if not url.startswith("git+") else ""
    spec_url = f"{prefix}{url}@{ref}#egg={__pkg_name__}"
    logger.debug("Constructed pip spec: %s", spec_url)
    return spec_url


def self_upgrade(reset=False, freeze=False, rev: str | None = None) -> int:
    """
    upgrade           : branch -> latest; sha -> same; semver tag -> latest semver
    upgrade --reset   : ignore current ref, use latest semver tag
    upgrade X: explicitly switch to branch/tag/sha X
    upgrade --freeze X: pin to current ref (branch/tag/sha)
    """

    # installs are always forced to avoid skipping of moving branches,
    # if pip thinks the package is already installed
    pip_args = ["install", "--upgrade", "--force-reinstall", "--no-cache-dir"]

    info = get_install_info()

    if not info.url:
        raise RuntimeError("Installation URL must be specified")

    if not info.is_vcs or info.url.startswith("file://"):
        raise RuntimeError(
            "Non-Git installation of hooked detected; remove and re-install via Git repository."
        )

    # read all tags from remote via git
    tags = git_get_tags(info.url)

    # by default target_ref is latest semver release
    target_ref = get_latest_release(tags)
    if not target_ref:
        raise RuntimeError(
            "Could not determine latest semver tag from remote repository."
        )

    if rev:
        logger.debug("Switching to pinned %s", rev)
        # we can not pin a tag directly, so we pin the sha of the tag
        # if non-sha is given with --pin, we pin the sha of the current commit
        # FIXME: breaks, if someone tries to pin a tag
        if _is_semver_tag(rev):
            target_ref = get_sha_for_tag(tags, rev)
        elif freeze:
            target_ref = git_get_last_branch_commit(info.url, rev)
        else:
            target_ref = rev
    # reset we keep the default target_ref of latest semver tag
    elif reset:
        # noop kept for clarity,
        # can be expanded in future if needed
        logger.debug("Resetting latest release %s", target_ref)
        pass
    # regular upgrade
    else:
        match info.requested_revision:
            case rev if _is_sha(rev):
                target_ref = info.commit
                logger.debug("Updating sha: %s", target_ref)
            case rev if _is_semver_tag(rev):
                target_ref = get_latest_release(tags)
                logger.debug("Updating semver tag: %s", target_ref)
            case rev if rev and not rev.startswith("v"):
                target_ref = info.requested_revision
                logger.debug("Updating branch: %s", target_ref)
            case _:
                # noop, keep default target_ref of latest semver tag
                logger.debug("regular upgrade to latest: %s", target_ref)
                pass

    spec = get_url_ref(info.url, target_ref)
    logger.debug("Specification: %s", spec)
    pip_args.append(spec)
    return _run_pip(*pip_args)


def get_last_upgrade_timestamp() -> datetime | None:
    """Reads last upgrade timestamp from hooked config directory"""

    ts_file = os.path.join(get_base_dir(), "last_upgrade.txt")

    try:
        with open(ts_file, encoding="utf-8") as f:
            ts = f.read().strip()
            ts = datetime.fromisoformat(ts)
            return ts
    except FileNotFoundError:
        return None


def set_last_upgrade_timestamp() -> None:
    """Writes last upgrade timestamp to hooked config directory"""

    ts_file = os.path.join(get_base_dir(), "last_upgrade.txt")
    ts = datetime.now().isoformat()

    with open(ts_file, "w", encoding="utf-8") as f:
        f.write(ts)
