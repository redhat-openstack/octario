# Octario

**Openstack Component Testing Ansible Roles**

Octario is a collection of Ansible roles and playbooks for testing Openstack Components on RHEL/CentOS/Fedora.

It supports the following testers:

* PEP8
* unit
* functional
* API

Coming Soon: Tempest.

## Requirements

1. ansible installed on the system ( ansible >= 2 ).
2. Component source code ( Can be downloaded using `git clone git://git.openstack.org/openstack/<component_name>.git` ).

`octario` is not provisioning the node on which it will run the tests. It's assumed
that the tester node is provided by the user by specifing it in the hosts file.

# How to run Octario

1. First, create an inventory file that will include the IP address or the hostname of your tester node.

```
vi hosts

[tester]
my_tester_host
```

2. Edit octario.cfg with your component details. Make sure to specify name and version!

```
component:
  name: nova
  version: 8
```

3. Run octario!. Choose one of testers and run the following command in octario root directory

```
ansible-playbook -vvv -i hosts playbooks/pep8.yml --extra-vars @octario.cfg
```

pep8.yml can be replaced with [unittest, functional, api, scenario].yml

You can also specify your own tester

```
export TESTER=my_new_cool_tester
ansible-playbook -vvv -i hosts playbooks/custom.yml --extra-vars @octario.cfg
```

## Configuration

There are 3 configuration files `octario` is using.
For each one of the configuration files, an detailed sample is included in `samples` directory.

### octario.cfg

Decides what is tested and what tasks should be skipped.

It Must include component name and RHOS version.

```
component:
  name: neutron
  version: 9 # RHOS 9 is based on mitaka
  config_file_name: component.cfg
```

### component.cfg

Controls how the component is tested.

with component.cfg you can specify what RPMs should be installed/removed, what pre commands
should be executed and what is the tests invocation command. All this can be specified per
tester (pep8, unittest, etc) or for all testers.

For certain components, an component.cfg file is located in components_config/<rhos release> directory.
If there is a component.cfg file there, octario will use it. If not, it will try to look for it in octario
root directory, component's root directory and /etc.

Detailed example for component.cfg can be found in samples directory.

### ansible.cfg

This part of Ansible project and isn't an octario configuration file.
You can learn more about it at [Ansible official site](http://docs.ansible.com/ansible/intro_configuration.html)
