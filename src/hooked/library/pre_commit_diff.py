from yaml import safe_load
import os
from .files import get_base_dir
from .logger import logger


def pre_commit_diff(file_path: str) -> str:
    """
    Compares the default hooked .pre-commit-config.yaml with the one at the given file path
    and returns a unified list of ids that are found in both files as string list, seperated by commas.

    Args:
        file_path (str): The path to the .pre-commit-config.yaml file to compare.
    """

    logger.debug(
        f"Comparing pre-commit config at {file_path} with default hooked config."
    )

    hooked_base_dir = get_base_dir()
    hooked_pre_commit_config = os.path.join(
        hooked_base_dir, 'config', '.pre-commit-config.yaml'
    )
    with open(hooked_pre_commit_config) as f:
        hooked_pre_commit = safe_load(f)

    repo_pre_commit_config = os.path.join(file_path)

    try:
        with open(repo_pre_commit_config) as f:
            repo_pre_commit = safe_load(f)

        hooked_ids = set()
        repo_ids = set()

        for repo in hooked_pre_commit.get('repos', []):
            hooked_ids.update({hook.get('id') for hook in repo.get('hooks', [])})
        logger.debug(f"Found {len(hooked_ids)} repo hook ids, {hooked_ids}")

        for repo in repo_pre_commit.get('repos', []):
            repo_ids.update({hook.get('id') for hook in repo.get('hooks', [])})
        logger.debug(f"Found {len(repo_ids)} repo hook ids, {repo_ids}")

        common_ids = hooked_ids.intersection(repo_ids)
        logger.debug(f"Found {len(common_ids)} common hook ids, {common_ids}")
        return ','.join(common_ids)

    except FileNotFoundError as e:
        logger.error(f"A file was not found: {e}")
        return ''
