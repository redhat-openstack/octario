#!/usr/bin/env python

import logger

LOG = logger.LOG


class OctarioException(Exception):
    """Base Octario Exception

    To use this class, inherit from it and define a
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.

    """

    msg_fmt = "An unknown exception occurred."

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        self.message = message
        if not self.message:
            try:
                self.message = self.msg_fmt % kwargs
            except Exception:
                # arguments in kwargs doesn't match variables in msg_fmt
                import six
                for name, value in six.iteritems(kwargs):
                    LOG.error("%s: %s" % (name, value))
                self.message = self.msg_fmt


class NotValidGitRepoException(OctarioException):
    def __init__(self, repo_path):
        msg = \
            "Git Repository not found under:  '{}'".format(
                repo_path)
        super(self.__class__, self).__init__(msg)


class NotValidComponentPathException(OctarioException):
    def __init__(self, component_path):
        msg = \
            "Component repository not found under:  '{}'".format(
                component_path)
        super(self.__class__, self).__init__(msg)


class NotValidComponentURL(OctarioException):
    def __init__(self, component_url):
        msg = \
            "Invalid Component URL:  '{}'".format(
                component_url)
        super(self.__class__, self).__init__(msg)


class InvalidRhosRelease(OctarioException):
    def __init__(self, branch_name):
        msg = \
            "Can't get RHOS version from branch:  '{}'".format(
                branch_name)
        super(self.__class__, self).__init__(msg)


class UnsupportedTester(OctarioException):
    def __init__(self, tester_type):
        from cli.tester import TesterType
        msg = \
            "Tester '{}' is not supported by Octario CLI.".format(
                tester_type)
        LOG.info("Supported testers: {}".format(
            TesterType.get_supported_testers()))
        super(self.__class__, self).__init__(msg)


class AnsiblePlaybookNotFound(OctarioException):
    def __init__(self, playbook_path):
        msg = \
            "Tester playbook not found:  '{}'".format(
                playbook_path)
        super(self.__class__, self).__init__(msg)


class CommandError(OctarioException):
    def __init__(self, msg):
        super(self.__class__, self).__init__(msg)
