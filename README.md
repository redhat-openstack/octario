# Octario

**Openstack Component Testing Ansible Roles**

Octario is a collection of Ansible roles and playbooks for testing OpenStack Components on RHEL/CentOS.

It supports the following testers or test frameworks:

* PEP8
* unit
* functional
* fullstack


There are two ways to use Octario. By cloning and installing Octario or by using the InfraRed framework.
We'll cover both.

Note: `octario` is not provisioning the node on which it will run the tests. It's assumed
      that the tester node is provided by the user by specifying it in the hosts file.

## Installation - without InfraRed

git clone https://github.com/redhat-openstack/octario && cd octario
virtualenv ~/octario_venv && source ~/octario_venv/bin/activate
pip install .

## Installation - with InfraRed

git clone https://github.com/redhat-openstack/infrared && cd infrared
virtualenv ~/ir_venv && source ~/ir_venv/bin/activate
pip install .
infrared plugin add octario

## Usage - without InfraRed

First, create an inventory file that will include the IP address or the hostname of your tester node.

```
vi hosts

[tester]
my_tester_host ansible_user=cloud-user
```

Edit `octario.yml` with your component details. Make sure to specify name and version!

```
component:
  name: nova
  version: 9
```

Run octario! :)
Choose one of testers and run the following command in octario root directory

```
ansible-playbook -vvv -i hosts playbooks/pep8.yml --extra-vars @octario.yml
```

pep8.yml can be replaced with [unittest, functional, fullstack].yml

## Usage - with InfraRed

```
infrared octario --t <tester_name> --dir <component_path>

For example:

infrared octario --t pep8 --dir $WORKSPACE/neutron
```


### Custom tester

You can specify your own tester

```
export TESTER=my_new_cool_tester
ansible-playbook -vvv -i hosts playbooks/custom-tester.yml --extra-vars @octario.yml
```

### External ROLES

You can use external role with `octario`.

```
cp -r new_role octario/roles
export ROLE=new_role
ansible-playbook -vvv -i hosts playbooks/custom-role.yml --extra-vars @octario.yml
```

## How it works

The following drawing added to simplify work-flow overview of `octario` for simple testers
as pep8, unittest and functional.

<div align="center"><img src="./doc/octario_workflow.png" alt="Octario work-flow"></div><hr />

### Patch RPMs

Patching of RPMs is deprecated in Octario.

Please use Octario as InfraRed plugin to achieve patching.

Using InfraRed and its' patch-components plugin instead, example:

 $ infrared plugin add patch-components
 $ infrared plugin add octario

 $ infrared patch-components --component-name neutron --component-path /patch/to/neutron/source/code --component-version 14
 $ infrared octario --t dsvm-functional --dir /patch/to/neutron/source/code

## More Docs

See the [/docs](https://github.com/redhat-openstack/octario/tree/master/docs) directory of this repo.
