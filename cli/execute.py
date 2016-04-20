import ansible.constants
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.utils.display import Display

from cli import conf, exceptions, logger

LOG = logger.LOG
CONF = conf.config


def ansible_playbook(playbook, verbose=2, settings=None,
                     inventory="hosts"):
    """Wraps the 'ansible-playbook' CLI.

     :param playbook: the playbook to invoke
     :param verbose: Ansible verbosity level
     :param settings: dict with Ansible variables.
     :param inventory: the inventory file to use, default: hosts
    """

    loader = DataLoader()
    variable_manager.set_inventory(inventory)

    playbook_executer = PlaybookExecutor(playbooks=[path_to_playbook],
                                         inventory=inventory,
                            variable_manager=variable_manager, loader=loader,
                            options=options, passwords=passwords)
    results = playbook_executer.run()
