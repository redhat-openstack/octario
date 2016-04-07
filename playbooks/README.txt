=== Introduction ===

octario/playbooks includes the playbooks needed to setup the remote node and run the tests.

=== Usage ===

First, run setup playbook:

ansible-playbook -i <hosts_file> setup.yml

Next, choose the tester you want to use:

ansible-playbook -i <hosts_file> [pep8, unittest, functional, api, scenario].yml

=== Notes ===

You can choose your own tester (= tox target) by:

export TESTER=dsvm-functional
ansible-playbook -i <hosts_file> custom.yml
