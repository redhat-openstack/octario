#!/usr/bin/env python

# Copyright 2016,2019 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from octario.lib import exceptions
from octario.lib import logger

import git
import os
import re

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse as urlparse

LOG = logger.LOG

GITREVIEW_FILENAME = ".gitreview"


class RepoType(object):
    """Enumeration for the repository type."""
    GIT, NONE = range(2)


class Component(object):
    """Representation of the component to be tested.

    Args:
        path (:obj:`str`): Path to directory where component is stored.
    """
    def __init__(self, path):
        self.path = path
        utils = ComponentUtils(path)
        self.component_name = utils.get_component_name()
        self.rhos_release = utils.get_rhos_release()
        self.rhos_release_repo = utils.get_rhos_release_repo()

    def get_name(self):
        """Return name of the component.

        Returns:
            str: component name
        """
        return self.component_name

    def get_rhos_release(self):
        """Return numeric value of rhos release of the component.

        Returns:
            str: RHOS release version
        """
        return self.rhos_release

    def get_rhos_release_repo(self):
        """rhos-release to be enabled based on the component branch name.

        Returns:
            str: rhos-release repository name as string
        """
        return self.rhos_release_repo


class ComponentUtils(object):
    """Utils for the component object.

    Various utils needed to discover information about component.

    Args:
        path (:obj:`str`): Path to directory where component is stored.
    """
    def __init__(self, path):
        self.path = path
        self.component_name = None
        self.rhos_release = None
        self.rhos_release_repo = None
        self.branch = None
        self.repo_type = self.__get_repo_type(self.path)

    def get_component_name(self):
        """Gets the name of the component.

        Returns:
            str: component name if exists or None if it wasn't discovered
        """
        if self.repo_type is RepoType.GIT:
            if not self.component_name:
                repo_url, self.branch = \
                    self.__get_branch_url_from_git(self.path)
                self.component_name = \
                    self.__get_component_name_from_git_url(repo_url)
        return str(self.component_name)

    def get_rhos_release(self):
        """Gets the name of the component.

        Returns:
            str: RHOS release version or None if it wasn't discovered
        """
        # this allows us to bypass detection algorithm which can fail in
        # few cases, like cherry picked changes.
        if 'RHOS_VERSION' in os.environ:
            return os.environ['RHOS_VERSION']

        if self.repo_type is RepoType.GIT:
            if not self.branch:
                repo_url, self.branch = \
                    self.__get_branch_url_from_git(self.path)
            if not self.rhos_release:
                self.rhos_release = \
                    self.__get_rhos_version_from_branch(self.branch)
        return str(self.rhos_release)

    def get_rhos_release_repo(self):
        """Gets the rhos-release repo name

        Returns:
            str: rhos-release repository name or None if it wasn't discovered
        """
        import pdb; pdb.set_trace()
        if self.repo_type is RepoType.GIT:
            if not self.branch:
                repo_url, self.branch = \
                    self.__get_branch_url_from_git(self.path)
            if not self.rhos_release:
                self.rhos_release = \
                    self.__get_rhos_version_from_branch(self.branch)
            if 'trunk' in self.branch:
                self.rhos_release_repo = str(self.rhos_release) + '-trunk'
            else:
                self.rhos_release_repo = str(self.rhos_release)

        return str(self.rhos_release_repo)

    def __get_repo_type(self, path):
        """Gets the repository type of the component.

        Raises:
            NotValidComponentPathException: If there is no valid path to the
            supported component type.

        Returns:
            (:obj:`RepoType`): Type of repository.
        """
        if os.path.isdir(os.path.join(path, '.git')):
            LOG.debug('Found GIT repository: %s' % path)
            return RepoType.GIT
        raise exceptions.NotValidComponentPathException(path)

    def __get_component_name_from_git_url(self, url):
        """Extracts component name from the git url.

        Name is calculated from last part of the URL by removing .git suffix.

        Raises:
            NotValidComponentURL: If there is no valid url found.

        Returns:
            str: component name
        """
        url_o = urlparse(url)

        if not url_o.scheme or not url_o.path or "/" not in url_o.path:
            raise exceptions.NotValidComponentURL(url)

        # path may start with /, so strip it
        r_index = url_o.path.rfind("/")
        component_name = url_o.path[r_index + 1:]

        suffix = ".git"
        if component_name.endswith(suffix):
            # Remove .git suffix
            component_name = component_name[:-len(suffix)]

        LOG.info('Component: %s' % component_name)

        return component_name

    def __get_branch_from_gitreview(self, path):
        """Gets branch from local .gitreview file.

        Args:
            path (:obj:`str`): Path to the git directory.

        Returns:
            str: branch name or None if branch name was not found
        """

        branch_name = None
        gitreview_path = os.path.join(path, GITREVIEW_FILENAME)

        try:
            with open(gitreview_path, 'r') as f_op:
                for line in f_op:
                    if 'defaultbranch=' in line:
                        default_branch = line.split("=", 1)[1]
                        r_index = default_branch.rfind("/")
                        branch_name = default_branch[r_index + 1:-1]
        except IOError as ex:
            # Log error in debug mode, but do nothing about this
            # because this is fallback method for getting branch name
            LOG.debug(ex)
            LOG.debug('Failed to get branch from %s' % gitreview_path)

        return branch_name

    def __get_branch_url_from_git(self, path):
        """Gets repo_url and branch from local git directory.

        Raises:
            NotValidGitRepoException: If there is no git directory found.

        Args:
            path (:obj:`str`): Path to the git directory.

        Returns:
            touple: repo URL and branch name from local git directory
        """
        repo_url = None
        branch_name = None

        try:
            g = git.Git(path)
            LOG.debug('Found remotes {}'.format(','.join([remote for remote in g.remote().split('\n')])))
            for remote_name in ('rhos', 'patches', 'origin'):
                if remote_name in g.remote().split('\n'):
                    repo_url = g.config("--get", "remote.{}.url".format(remote_name))
                    LOG.debug('Using Remote {}'.format(remote_name))
                    break
            if repo_url is None:
                raise exceptions.NotValidGitRepoException(path)

            repo = git.Repo(path)
            branch = repo.active_branch
            branch_name = branch.name
        except (git.exc.InvalidGitRepositoryError,
                git.exc.GitCommandNotFound,
                git.exc.GitCommandError) as git_ex:
            LOG.error(git_ex)
            raise exceptions.NotValidGitRepoException(path)
        except TypeError:
            # If not found directly from git, try to get the branch name
            # from .gitreview file which should be pointing to the proper
            # branch.
            LOG.debug('Fallback method to get branch name from .gitreview')
            branch_name = self.__get_branch_from_gitreview(path)
            if not branch_name:
                # Git repo is most likely in detached state
                # Fallback method of getting branch name, much slower
                LOG.debug('HEAD detached, fallback method to get branch name')
                head_branch = os.linesep.join(
                    [s for s in g.log('--pretty=%d').splitlines()
                     if s and "tag:" not in s])
                r_index = head_branch.rfind("/")
                branch_name = head_branch[r_index + 1:-1]

        LOG.debug('Component repository: %s' % repo_url)
        LOG.debug('Component branch: %s' % branch_name)

        return repo_url, branch_name

    def __get_rhos_version_from_branch(self, branch_name):
        """Gets rhos release version from branch name.

        Raises:
            InvalidRhosRelease: No RHOS release found within branch name.

        Args:
            branch_name (:obj:`str`): Branch name.

        Returns:
            str: RHOS release version
        """
        # bypass for CR branches.
        if 'RHOS_VERSION' in os.environ:
            rhos_release = os.environ['RHOS_VERSION']
        else:
            rhos_release = re.findall(r'[0-9][0-9]?\.[0-9]', branch_name)

        # Unexpected parsing of branch name
        if len(rhos_release) != 1:
            raise exceptions.InvalidRhosRelease(branch_name)

        major_version, minor_version = rhos_release[0].split(".")[:2]
        if minor_version == '0' and int(major_version) < 17:
            rhos_release = major_version
        else:
            rhos_release = '%s.%s' % (major_version, minor_version)

        LOG.info('RHOS release: %s' % rhos_release)

        return rhos_release
