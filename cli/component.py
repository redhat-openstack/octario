#!/usr/bin/env python

import exceptions
import logger

import git
import os
import re

from urlparse import urlparse

LOG = logger.LOG


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
        return self.component_name

    def get_rhos_release(self):
        """Gets the name of the component.

        Returns:
            str: RHOS release version or None if it wasn't discovered
        """
        if self.repo_type is RepoType.GIT:
            if not self.branch:
                repo_url, self.branch = \
                    self.__get_branch_url_from_git(self.path)
            if not self.rhos_release:
                self.rhos_release = \
                    self.__get_rhos_version_from_branch(self.branch)
        return self.rhos_release

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
            repo_url = g.config("--get", "remote.origin.url")
            repo = git.Repo(path)
            branch = repo.active_branch
            branch_name = branch.name
        except (git.exc.InvalidGitRepositoryError,
                git.exc.GitCommandNotFound,
                git.exc.GitCommandError) as git_ex:
            LOG.error(git_ex)
            raise exceptions.NotValidGitRepoException(path)
        except TypeError:
            # Git repo is most likely in detached state
            # Fallback method of getting branch name, much slower
            head_branch = g.log('--pretty=%d').splitlines()[0]
            r_index = head_branch.rfind("/")
            branch_name = head_branch[r_index + 1:-1]

        LOG.debug('Component repository: %s' % repo_url)
        LOG.debug('Component branch: %s' % branch)

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
        rhos_release = re.findall('[0-9][0-9]?\.[0-9]', branch_name)

        # Unexpected parsing of branch name
        if len(rhos_release) != 1:
            raise exceptions.InvalidRhosRelease(branch_name)

        rhos_release = rhos_release[0].split(".")[0]

        LOG.info('RHOS release: %s' % rhos_release)

        return rhos_release
