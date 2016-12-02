#!/usr/bin/env python

import exceptions
import logger

from enum import Enum
import os

LOG = logger.LOG


class TesterType(Enum):
    PEP8 = 'pep8'
    FUNCTIONAL = 'functional'
    UNIT = 'unit'
    NONE = ''

    def __str__(self):
        return str(self.value)


class Tester(object):
    def __init__(self, tester):
        self.type = self.__get_tester_type(tester)
        self.playbook_path = self.__get_playbbok_path()

    def get_type(self):
        return self.type

    def get_playbook_path(self):
        return self.playbook_path

    def __get_playbbok_path(self):
        script_path = os.path.dirname(os.path.abspath(__file__))
        playbook_path = os.path.join(script_path, "..", "playbooks",
                                     str(self.type) + ".yml")

        if not os.path.isfile(playbook_path):
            LOG.error("Tester playbook not found: %s" % playbook_path)
            raise exceptions.UnsupportedTester(str(self.type))

        LOG.debug("Tester playbook: %s" % playbook_path)

        return playbook_path

    def __get_tester_type(self, tester):
        if not tester:
            raise exceptions.UnsupportedTester('Unknown')

        for tester_type in TesterType:
            if tester.lower() == tester_type.value:
                return tester_type

        raise exceptions.UnsupportedTester(tester)
