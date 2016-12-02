#!/usr/bin/env python

import exceptions
import logger

from enum import Enum
import os

LOG = logger.LOG


class TesterType(Enum):
    """Enum for the tester type supported by octario CLI.

    Tester type name must match the playbook filename
    """
    PEP8 = 'pep8'
    FUNCTIONAL = 'functional'
    UNIT = 'unit'
    NONE = ''

    def __str__(self):
        return str(self.value)


class Tester(object):
    """Representation of the tester.

    Object holds information about tester type and relevant attributes
    required to run tester such as playbook for that tester.

    Args:
        tester (:obj:`str`): string value of the tester e.g. 'pep8'
    """
    def __init__(self, tester):
        self.type = self.__get_tester_type(tester)
        self.playbook_path = self.__get_playbook_path()

    def get_type(self):
        """Gets type of the tester.

        Returns:
            (:obj:TesterType): tester type
        """
        return self.type

    def get_playbook_path(self):
        """Get path to the playbook for the tester.

        Returns:
            str: tester playbook path
        """
        return self.playbook_path

    def __get_playbook_path(self):
        """Calculates the playbook path based on the octario module path.

        Raises:
            UnsupportedTester: If there is no playbook associated with the
            tester. Playbook filename must match tester name.

        Returns:
            str: tester playbook path
        """
        script_path = os.path.dirname(os.path.abspath(__file__))
        playbook_path = os.path.join(script_path, "..", "playbooks",
                                     str(self.type) + ".yml")

        if not os.path.isfile(playbook_path):
            LOG.error("Tester playbook not found: %s" % playbook_path)
            raise exceptions.UnsupportedTester(str(self.type))

        LOG.debug("Tester playbook: %s" % playbook_path)

        return playbook_path

    def __get_tester_type(self, tester):
        """Returns tester type based on the passed tester type string.

        Raises:
            UnsupportedTester: If the tester is not in the supported testers
            enumeration.

        Args:
            tester (:obj:`str`): string value of the tester e.g. 'pep8'

        Returns:
            (:obj:TesterType): tester type
        """
        if not tester:
            raise exceptions.UnsupportedTester('Unknown')

        for tester_type in TesterType:
            if tester.lower() == tester_type.value:
                return tester_type

        raise exceptions.UnsupportedTester(tester)
