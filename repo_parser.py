#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Parser pages and export repo json file.
"""

import os
import json
import requests
import time
import logging
import itertools
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from logging.handlers import RotatingFileHandler

class RepoParser(object):
    def __init__(self, excludes=[]):
        self.connection_timeout = 15
        self.read_timeout = 15
        self.retry = 3
        self.retry_interval = 3
        self.repo = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        self.log_file = RotatingFileHandler(self.__class__.__name__+".log", maxBytes=1024 * 1024, backupCount=3)
        # self.log_file.setLevel(logging.DEBUG)
        self.log_file.setFormatter(self.formatter)
        self.console = logging.StreamHandler()
        # self.console.setLevel(logging.DEBUG)
        self.console.setFormatter(self.formatter)
        self.logger.addHandler(self.log_file)
        self.logger.addHandler(self.console)
        self.excludes = excludes
        self.export_file_name = "repos.json"

    def download_page(self, url):
        """
        Download the url.

        :param url: the url for download
        :returns: url content or None
        """

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/80.0.3987.163 Safari/537.36"}
        retry = 0
        r = None
        while retry <= self.retry:
            try:
                r = requests.get(url, headers=headers, timeout=(self.connection_timeout, self.read_timeout))
                r.encoding = 'utf-8'
                return r.text
            except requests.exceptions.RequestException as e:
                retry += 1
                self.logger.error(e)
                time.sleep(self.retry_interval)
        self.logger.error("download page failed: %s", url)
        return r

    def export_json(self, path=""):
        """
        Export repo list to json file

        :param path: file path to save
        """
        file = os.path.join(path, self.export_file_name)
        if self.repo:
            with open(file, 'w') as f:
                json.dump(self.repo, f, indent=2, ensure_ascii=False)
        else:
            self.logger.error("Empty repo list")

    def parser(self):
        """
        Dummy function, need to be rewrite by inheritance class
        """

        self.logger.error("Rewrite me")

    def matches_excludes(self, url):
        """
        Return if this URL matches an exclude.

        :param url: The URL to check,  return True if matching
        """

        base = url.split("/")[-1] or url.split("/")[-2]
        base_without_git = base.split(".")[0]
        return base in self.excludes or base_without_git in self.excludes


class YoctoRepoParser(RepoParser):
    def __init__(self, entry_url, excludes=[]):
        super().__init__(excludes)
        self.entry_url = entry_url
        self.export_file_name = "yocto_repos.json"

    def parser(self):
        self.repo = self.parser_mainpage(self.entry_url)
        if not self.repo:
            self.logger.error("No repo in this page %s", self.entry_url)
            return
        for item in self.repo:
            if not item["url"]:
                continue
            repo_urls = self.parser_repo_page(item["url"])
            if repo_urls:
                item["git"] = repo_urls["git"]
                item["https"] = repo_urls["https"]
            if item["git"] or item["https"]:
                del item["url"]
                self.logger.info("Complete: %s", item)
            else:
                self.logger.warning("Uncomplete: %s", item)

    def parser_mainpage(self, url):
        data = []
        html = self.download_page(url)
        repo_section = ""
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', attrs={'class': 'list nowrap'})
            if table:
                for row in table.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) == 0:
                        continue
                    if len(cols) == 1:
                        repo_section = cols[0].text.strip()
                        continue
                    url = ""
                    for link in cols[0].find_all('a', href=True):
                        url = urljoin(self.entry_url, link['href'])
                    if self.matches_excludes(url):
                        self.logger.info("Skipping %s as it matches an exclude", url)
                        continue
                    cols = [ele.text.strip() for ele in cols]
                    item = {
                        "name": cols[0],
                        "section": repo_section,
                        "description": cols[1],
                        "owner": cols[2],
                        "url": url,
                        "git": "",
                        "https": ""
                    }
                    data.append(item)
        return data

    def parser_repo_page(self, url):
        html = self.download_page(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', attrs={'class': ['list nowrap', 'list']})
            if table:
                for row in table.find_all('tr'):
                    if row.text.strip() == "Clone":
                        repo_urls = {
                            "git": "",
                            "https": ""
                        }
                        for element in row.next_siblings:
                            repo_url = element.string
                            if repo_url.startswith("git:"):
                                repo_urls["git"] = repo_url
                            if repo_url.startswith("https:"):
                                repo_urls["https"] = repo_url
                        return repo_urls
        return None


class GitHubRepoParser(RepoParser):
    def __init__(self, user, excludes=[]):
        super().__init__(excludes)
        self.user = user
        self.export_file_name = "github_" + self.user + "_repos.json"

    def parser(self):
        for page in itertools.count(start=1):
            url = "https://api.github.com/users/%s/repos?page=%d" % (self.user, page)
            res = self.download_page(url)
            if res:
                res_json = json.loads(res)
                if not res_json:
                    break
                for repo in res_json:
                    if self.matches_excludes(repo["clone_url"]):
                        continue
                    item = {
                        "name": repo["name"],
                        "description": repo["description"],
                        "owner": repo["owner"]["login"],
                        "git": repo["git_url"],
                        "https": repo["clone_url"]
                    }
                    self.logger.info("Complete: %s", item)
                    self.repo.append(item)
            else:
                self.logger.error("Stop at page %s", page)
                break


def yocto():
    main_page = "http://git.yoctoproject.org/cgit.cgi/"
    excludes = ["yocto-testresults"]
    repo = YoctoRepoParser(main_page, excludes)
    repo.parser()
    repo.export_json()


def github(user):
    repo = GitHubRepoParser(user)
    repo.parser()
    repo.export_json()


if __name__ == "__main__":
    github("d12y12")
