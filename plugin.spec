plugin_type: test
description: Octario test runner
subparsers:
    octario:
        help: Octario test runner
        description: Octario test runner
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
                      type: VarDir
                      help: "Path to component directory"
                      required: yes
                  dest-dir:
                      type: VarDir
                      help: "Path to use for collected files. Defaults to CWD."
                      required: no
                      default: ''
                  tester-host:
                      type: Value
                      help: Inventory host to use as tester
                  tester-group:
                      type: Value
                      help: Inventory group to use as tester(s)
