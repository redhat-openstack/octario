#!/usr/bin/env python

# Copyright 2016 Red Hat, Inc.
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
from os.path import basename

import glob
import os

LOG = logger.LOG

DEFAULT_TESTERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   '..', 'ansible', 'playbooks')


class TesterType(object):
    """Tester types supported by octario CLI.

    """

    @classmethod
    def get_supported_testers(cls):
        """Get list of supported testers as strings.

        Args:
            cls (:obj:`TesterType`): Class itself

        Returns:
            list: List of supported testers
        """
        supported_testers = []
        for playbook in glob.glob(os.path.join(DEFAULT_TESTERS_DIR, "*.yml")):
            tester = basename(playbook.split(".yml")[0])
            supported_testers.append(str(tester))
        return sorted(supported_testers)


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
            AnsiblePlaybookNotFound: If there is no playbook associated
            with the tester. Playbook filename must match tester name.

        Returns:
            str: tester playbook path
        """
        playbook_path = os.path.join(DEFAULT_TESTERS_DIR,
                                     str(self.type) + ".yml")

        if not os.path.isfile(playbook_path):
            raise exceptions.AnsiblePlaybookNotFound(playbook_path)

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

        for tester_type in TesterType.get_supported_testers():
            if tester.lower() == tester_type.lower():
                return tester_type

        raise exceptions.UnsupportedTester(tester)
