#!/bin/bash
# THIS CAN BE CALLED FROM INSIDE TOX, assumes already existing venv
#
# This script would test octario by provisioning a test
# machine, running octario on it (pep8) for a one component and
# deprovisionign it.
set -exuo pipefail
if [ -z ${DNS+x} ]; then
  echo "WARN: internal DNS environment value not found, running tests without it may cause failures";
else
  IR_DNS=--dns=${DNS}
fi

if [ -z ${OS_CLOUD+x} ]; then
  echo "WARN: internal OS_CLOUD environment value not found, running tests without it may cause failures";
else
  IR_CLOUD=--cloud=${OS_CLOUD}
fi

# code to determine a meaningful prefix for both CLI and CI use cases
HIGHLIGHT='\033[01;32m'
NORMAL='\033[0m'
email=`git config user.email`
username=${email%\@*}
PREFIX=$username-octario-`echo -n '${BUILD_TAG:-$USER}' | md5sum | cut -c1-4`-
# making prefix safe for being used as part of hostname
PREFIX=$(echo $PREFIX | sed "s/[^a-z|0-9]\-//g;")
export PREFIX
export ANSIBLE_VERBOSITY=0
export ANSIBLE_HOST_KEY_CHECKING=False
export ANSIBLE_STDOUT_CALLBACK=minimal
export ANSIBLE_STDOUT_CALLBACK=oneline
#export ANSIBLE_STDOUT_CALLBACK=debug

# infrared can currently only function if is called from its own install dir
IR_DIR=$(python -c 'import os, infrared; print(os.path.abspath(os.path.join(os.path.dirname(infrared.__file__),"..")))')
pushd $IR_DIR

echo -e "Using prefix ${HIGHLIGHT}${PREFIX}${NORMAL} and running from ${HIGHLIGHT}${IR_DIR}${NORMAL} ..."

infrared octario --help >/dev/null

for KEY in ~/.ssh/rhos-jenkins/id_rsa ~/.ssh/id_rsa
do
    if [ -f ~/.ssh/rhos-jenkins/id_rsa ]; then
        break
    fi
done

ansible --version
infrared --version

# provision resources (future: skip running if already provisioned)
infrared openstack --topology-nodes=tester:1 \
--topology-network=3_nets \
--image=rhel-7.4-server-x86_64-updated \
${IR_CLOUD:-} \
--prefix=$PREFIX \
--key-file=$KEY \
${IR_DNS:-}
# now we need one reference component to test with
if [ ! -d ../cinder ]; then
  git clone https://code.engineering.redhat.com/gerrit/cinder --branch rhos-11.0-patches --single-branch ../cinder
fi

infrared octario --t pep8 --dir ../cinder


#infrared
#infrared --help
#ir octario --t pep8 --dir ../cinder