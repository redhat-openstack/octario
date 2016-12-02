#!/usr/bin/env python

import os

from ansible.cli.playbook import PlaybookCLI

import exceptions
import logger
import logging

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

        ansible_cli = PlaybookCLI(self.cli_args)
        ansible_cli.parse()
        results = ansible_cli.run()

        if results:
            raise exceptions.CommandError("Failed to run tester: %s" %
                                          self.tester.get_playbook_path())

        return results

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
            inventory_fallback = os.path.join(script_path, "..", "local_hosts")
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
