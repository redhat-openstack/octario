=== Introduction ===

octario/playbooks includes the playbooks needed to setup the remote node and run the tests.

playbooks/setup  -> the playbook for setting up the environment (repos, packages, etc).
playbooks/tester -> the playbooks for running specific tester (pep8, unittest, functional, etc).

=== Usage ===

First, run the playbook in setup directory to setup the environment:

ansible-playbook -i <hosts_file> playbooks/setup/setup_environment.yml

Next, run the tester you want to use:

ansible-playbook -i <hosts_file> [pep8, unittest, functional, api, scenario].yml

=== Notes ===

You can specify your own tester (= tox target) with:

export TESTER=dsvm-functional
ansible-playbook -i <hosts_file> custom.yml
