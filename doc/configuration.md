# Configuration

There are 3 configuration files `octario` is using.
For each one of the configuration files, an detailed sample is included in `samples` directory.

### octario.yml

Decides what is tested and what tasks should be skipped.

It Must include component name and RHOS version.

```
component:
  name: neutron
  version: 9 # RHOS 9 is based on mitaka
  config_file_name: component.yml
```

### component.yml

Controls how the component is tested.

With `component.yml` you can specify what RPMs should be installed/removed, what pre commands
should be executed and what is the tests invocation command. All this can be specified per
tester (pep8, unittest, etc) or for all testers.

For certain components, an `component.yml` file is located in components_config/<rhos release> directory.
If there is a `component.yml` file there, octario will use it. If not, it will try to look for it in octario
root directory, component's root directory and /etc.

Detailed example for `component.yml` can be found in samples directory.

### ansible.cfg

This part of Ansible project and isn't an octario configuration file.
You can learn more about it at [Ansible official site](http://docs.ansible.com/ansible/intro_configuration.html)
