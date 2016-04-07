=== Introduction ===

octario/playbooks includes the playbooks needed to setup the remote node and run the tests.

=== Usage ===

Choose testr and run the following command:

ansible-playbook -i <hosts_file> [pep8, unittest, functional, api, scenario].yml

=== Notes ===

You can specify your own tester (= tox target) with:

export TESTER=dsvm-functional
ansible-playbook -i <hosts_file> custom.yml
