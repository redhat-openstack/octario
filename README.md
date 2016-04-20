# Octario

**Openstack Component Testing Ansible Roles**

Octario is a collection of Ansible roles and playbooks for testing Openstack Components on RHEL/CentOS/Fedora.

It supports the following testers:

* PEP8
* unit
* functional
* API

## Requirements

1. ansible installed on the system ( >=2 ).
2. component source code + component configuration file

`octario` is not provisioning the node on which it will run the tests. It's assumed
that the tester node is provided by the user by specifing it in the hosts file.

# Configuration

There are 3 configuration files.
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

Detailed example for component.cfg can be found in samples directory.

### ansible.cfg

This part of Ansible project and isn't an octario configuration file.
You can learn more about it at [Ansible official site](http://docs.ansible.com/ansible/intro_configuration.html)

## Run octario

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

3. Edit component.cfg to fit your component requirements.

4. Export rhos-release server IP address or hostname. This is needed in order for Octario run properly.

```
export rhos_release_server=<rhos-relese server IP address or hostname>
```

4. Run octario!. Choose one of testers and run the following command in octario root directory

```
ansible-playbook -vvv -i hosts playbooks/pep8.yml --extra-vars @octario.cfg
```

pep8.yml can be replaced with [unittest, functional, api, scenario].yml

You can also specify your own tester

```
export TESTER=my_new_cool_tester
ansible-playbook -vvv -i hosts playbooks/custom.yml --extra-vars @octario.cfg
```

# Octario CLI

Octario has cli that allows you to run tests using one command, without modifying
octario.cfg

### Examples

run tests for neutron component, rhos 8 release

```
cli/main.py --component neutron --rhos-release 8
```
