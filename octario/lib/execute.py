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

import logging
import os

LOG = logger.LOG


class AnsibleExecutor(object):
    """Executor for the ansible playbooks

    Used to run ansible CLI with the parameters needed for testing
    component by specified tester.

    Args:
        tester (:obj:`Tester`): Supported by octario CLI tester
        component (:obj:`Component`): Tested component
        inventory_file (:obj:`str`): Path to inventory file, defaults to
                                     'local_hosts' if file not found.
    """

    def __init__(self, tester, component, inventory_file):
        self.tester = tester
        self.component = component
        inventory_file_path = self.__get_inventory_file(inventory_file)
        self.cli_args = self.__get_ansible_playbook_args(inventory_file_path)

    def run(self):
        """Runs ansible CLI.

        Runs ansible CLI using PlaybookCLI and command line arguments
        stored in the self.cli_args list.

        Raises:
            CommandError: If there was error while running the command.

        Returns:
            int or list: return from the ansible PlaybookExecutor run()
        """

        # Set the ansible.cfg that will be used by octario
        octario_ansible_config = self._get_ansible_config_file()
        if octario_ansible_config:
            os.environ['ANSIBLE_CONFIG'] = octario_ansible_config

        # Import must happen after setting ANSIBLE_CONFIG, otherwise
        # environment variable will not be used.
        from ansible.cli.playbook import PlaybookCLI
        ansible_cli = PlaybookCLI(self.cli_args)
        ansible_cli.parse()
        results = ansible_cli.run()

        if results:
            raise exceptions.CommandError("Failed to run tester: %s" %
                                          self.tester.get_playbook_path())

        return results

    def _get_ansible_config_file(self):
        """Return path to the ansible config file

        Overrides default ansible config file from:
            lib/ansible/constants.py:load_config_file()

        Function returns None if either environment variable ANSIBLE_CONFIG
        exists or current working dir contains ansible.cfg file.
        This allows to fallback to default ansible method of gathering
        ansible.cfg file, while third option to use ansible.cfg from Octario
        installation path is used if no specific ansible.cfg was provided.

        Returns:
            str or None: path to the ansible.cfg cnfiguration file or None
                 if the file was provided via ANSIBLE_CONFIG or it exists
                 in the current working dir.
        """
        ansible_config_env = os.getenv("ANSIBLE_CONFIG", None)
        if ansible_config_env is not None:
            ansible_config_env = os.path.expanduser(ansible_config_env)
            if os.path.isdir(ansible_config_env):
                ansible_config_env += "/ansible.cfg"

        # Configuration file was found in the ANSIBLE_CONFIG env
        # Return None to fallback to standard ansible method
        if ansible_config_env and os.path.isfile(ansible_config_env):
            LOG.info('Using ansible config from ANSIBLE_CONFIG env: {}'.format(
                ansible_config_env))
            return None

        try:
            ansible_config_env = os.getcwd() + "/ansible.cfg"

            # Configuration file was found in the current working dir
            if ansible_config_env and os.path.isfile(ansible_config_env):
                LOG.info('Using ansible config from current dir: {}'.format(
                    ansible_config_env))
                return None
        except OSError:
            pass

        ansible_config_env = os.path.dirname(os.path.abspath(__file__))
        ansible_config_env = os.path.join(ansible_config_env, "../ansible/")

        LOG.debug('Using ansible config from default location: {}'.format(
            ansible_config_env))

        return ansible_config_env

    def __get_inventory_file(self, inventory_file):
        """Return path to the inventory file

        Returns passed inventory file path or the default fallback
        if the inventory file is not available.

        Args:
            inventory_file (:obj:`str`): Path to inventory file, defaults to
                                         'local_hosts' if file not found.

        Returns:
            str: path to the inventory file that will be used
        """
        if not os.path.isfile(inventory_file):
            LOG.warning("Inventory file does not exists: %s" % inventory_file)
            script_path = os.path.dirname(os.path.abspath(__file__))
            inventory_fallback = os.path.join(script_path, "../ansible/",
                                              "local_hosts")
            LOG.warning("Falling back to inventory: %s" % inventory_fallback)
            return inventory_fallback
        return inventory_file

    def __get_ansible_playbook_args(self, inventory_file):
        """Composes list of all arguments that will be used for running play.

        Function that gets all arguments that will be passed to the
        ansible-play CLI. The arguments are based on the tester and
        component objects and their variables taken from the public functions.

        To be consistent with the octario run ansible verbosity level
        is calculated from octario logger level.


        Args:
            inventory_file (:obj:`str`): Path to inventory file.

        Returns:
            list: arguments for the ansible CLI
        """

        verbose_level = "-vvv"
        if LOG.getEffectiveLevel() >= logging.INFO:
            verbose_level = "-v"

        extra_vars = {}
        extra_vars['component'] = dict(
            name=self.component.get_name(),
            version=self.component.get_rhos_release()
        )

        cli_args = ['execute', self.tester.get_playbook_path(), verbose_level,
                    '--inventory', inventory_file, '--extra-vars', extra_vars]

        LOG.debug('Ansible CLI args: {}'.format(cli_args[1:]))

        return cli_args
