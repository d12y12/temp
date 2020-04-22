#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Mirror git repositories from url, maintaining metadata.

This can be useful when maintaining a local mirror.
"""

import os
import stat
import json
import shutil
import subprocess
import logging
import argparse
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("git-mirror")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
log_file = RotatingFileHandler("git-mirror.log", maxBytes=1024*1024, backupCount=3)
# log_file.setLevel(logging.DEBUG)
log_file.setFormatter(formatter)
console = logging.StreamHandler()
# console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(log_file)
logger.addHandler(console)


def get_repo_dir_from_url(url):
    """
    Extract repo directory from url and Complete it with .git if the repo url not content it

    :param url: the url for the repo
    :returns: repo directory with .git
    """
    repo_dir = os.path.basename(url)
    name, ext = os.path.splitext(repo_dir)
    if ext is not "git":
        repo_dir = repo_dir + ".git"
    return repo_dir


def repo_already_mirrored(url):
    """
    Check if a repo is already mirrored.

    :param url: the url for the repo
    :returns: a bool denoting whether the dir for this repo exists
    """
    repo_dir = get_repo_dir_from_url(url)
    return os.path.isdir(repo_dir)


def update(repo):
    """
    Update a local mirror.

    :param repo: information about this repo
    """

    repo_dir = get_repo_dir_from_url(repo["https"])
    subprocess.check_call(["git", "--git-dir", repo_dir, "remote", "update", "--prune"])
    description(os.path.join(repo_dir, "description"), repo["description"])
    export(os.path.join(repo_dir, "git-daemon-export-ok"))


def mirror(repo):
    """
    Mirror a Git repository, maintaining metadata.

    :param repo: information about the repo to mirror
    """

    subprocess.check_call(["git", "clone", "--mirror", repo["https"]])

    repo_dir = get_repo_dir_from_url(repo["https"])
    description_file = os.path.join(repo_dir, "description")
    export_file = os.path.join(repo_dir, "git-daemon-export-ok")

    description(description_file, repo["description"])
    export(export_file)


def export(export_file):
    """
    Mark a repository as exportable.

    :param export_file: the path to the git-daemon-export-ok file
    """

    open(export_file, "a").close()


def description(description_file, description):
    """
    Update a description file for a git repo.

    :param description_file: the path to the description file
    :param description: the description for this repo
    """

    if description is not None:
        with open(description_file, "wb") as f:
            f.write(description.encode("utf8") + b"\n")


def remotely_deleted_repos(remote_repos):
    """
    Return a list of all repos existing locally, but not remotely.

    :param remote_repos: the names of all repos to check
    """

    files = os.listdir(".")

    local_repos = [x for x in files if x.endswith(".git") and x != ".git"]
    remote_repo_urls = [remote_repo["https"] for remote_repo in remote_repos]
    remote_repos = [get_repo_dir_from_url(url) for url in remote_repo_urls]
    return [repo for repo in local_repos if repo not in remote_repos]


def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def sync_repos(file, delete=False):
    """
    For each repo in the file, either update it if it is already mirrored, or
    mirror it

    :param file: the file to get the repositories for
    :param delete: delete remotely deleted repositories from our local mirror
    """

    with open(file, 'r') as f:
        user_repos = json.load(f)

    for repo in user_repos:
        url = repo["https"]
        if repo_already_mirrored(url):
            logger.info("Update: %s", url)
            update(repo)
        else:
            logger.info("Mirror: %s", url)
            mirror(repo)

    if delete:
        repos_to_delete = remotely_deleted_repos(user_repos)
        for repo in repos_to_delete:
            logger.info("Delete: %s", repo)
            shutil.rmtree(repo, onerror=remove_readonly)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-d", "--delete", action="store_true",
                        help="delete remotely deleted repositories from local mirror")
    parser.add_argument("file", help="file path content repos to mirror")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sync_repos(args.file, delete=args.delete)
