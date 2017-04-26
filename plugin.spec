plugin_type: test
subparsers:
    octario:
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
                      type: Value
                      help: "Path to component directory"
                      required: yes
