plugin_type: test
description: Octario test runner
subparsers:
    octario:
        help: Octario test runner
        include_groups: ['Ansible options', 'Inventory', 'Common options', 'Answers file']
        groups:
            - title: Octario
              options:
                  t:
                      metavar: TESTER
                      type: Value
                      help: "Octario tester to be ran."
                      required: yes
                  dir:
                      type: Value
                      help: "Path to component directory"
                      required: yes
