=== Introduction ===

octario/playbooks includes the playbooks used for running the different testers in addition to supportive playbooks such as collect_logs

=== Usage ===

Choose testr and run the following command:

ansible-playbook -i <hosts_file> testers/[pep8, unittest, functional, api, scenario].yml --extra-vars @octario.cfg

=== Notes ===

You can specify your own tester (= tox target) with:

export TESTER=dsvm-functional
ansible-playbook -i <hosts_file> custom.yml --extra-vars @octario.cfg
