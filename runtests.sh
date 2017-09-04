#!/bin/bash
# THIS CAN BE CALLED FROM INSIDE TOX, assumes already existing venv
#
# This script would test octario by provisioning a test
# machine, running octario on it (pep8) for a one component and
# deprovisionign it.
set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

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

if [ -z ${COMPONENT_PATH+x} ]; then
  if [ -z ${COMPONENT_URL+x} ]; then
    echo "WARN: git COMPONENT_URL and/or COMPONENT_BRANCH were not specified, we will assume PWD" \
    " already contains the cloned component/branch."
    COMPONENT_PATH=.
  else
    # build folder is already excluded from linters
    COMPONENT_PATH=$DIR/build/component
    rm -rf ${COMPONENT_PATH}
    mkdir -p $COMPONENT_PATH
    git clone $COMPONENT_URL --branch $COMPONENT_BRANCH --single-branch $COMPONENT_PATH
  fi
fi
# makes COMPONENT_PATH full path (readlink is not portable)
COMPONENT_PATH="$(cd ${COMPONENT_PATH}; pwd)"
echo "INFO: COMPONENT_PATH=$COMPONENT_PATH"

if [ -z ${COMPONENT_TESTER+x} ]; then
  echo "WARN: COMPONENT_TESTER was not defined, we will assume 'pep8'."
  COMPONENT_TESTER=pep8
fi

if [ -z ${KEY+x} ]; then
  for FILE in ~/.ssh/rhos-jenkins/id_rsa ~/.ssh/id_rsa
  do
      if [ -f $FILE ]; then
          export KEY=$FILE
          break
      fi
  done
fi

# code to determine a meaningful prefix for both CLI and CI use cases
HIGHLIGHT='\033[01;32m'
NORMAL='\033[0m'
PREFIX=$USER-octario-`echo -n '${BUILD_TAG:-$USER}' | md5sum | cut -c1-4`-
# making prefix safe for being used as part of hostname
# prefix is also stable between executions outside CI, allowing reuse of
# already provisioned machines (when DISABLE_CLEANUP=true)
PREFIX=$(echo $PREFIX | sed "s/[^a-z|0-9]\-//g;")
export PREFIX
export ANSIBLE_VERBOSITY=0
export ANSIBLE_HOST_KEY_CHECKING=False
#export ANSIBLE_STDOUT_CALLBACK=minimal
export ANSIBLE_FORCE_COLOR=1
#export ANSIBLE_STDOUT_CALLBACK=oneline
#export ANSIBLE_STDOUT_CALLBACK=debug

# projects from risk of inheriting user inventory, still if
# infrared default workspace happens to be the same, it may still re-use it,
# but this is seen as a feature, not a bug.
unset ANSIBLE_INVENTORY

# infrared can currently only function if is called from its own install dir
IR_DIR=$(python -c 'import os, infrared; print(os.path.abspath(os.path.join(os.path.dirname(infrared.__file__),"..")))')

PWD_ORIG=`pwd`
function finish {
  rv=$?
  # we restore previous working directory regardless the outcome
  cd $PWD_ORIG
  exit $rv
}
trap finish EXIT

pushd $IR_DIR >>/dev/null

  echo -e "INFO: Using prefix ${HIGHLIGHT}${PREFIX}${NORMAL} and running from ${HIGHLIGHT}${IR_DIR}${NORMAL} ..."

  # avoid provisioning in case octario is deeply broken
  infrared octario --help >/dev/null

  pip check > func.log || true
  pip freeze > func.log || true

  echo -e "INFO: infrared:${HIGHLIGHT}$(infrared --version 2>&1)${NORMAL} ansible:${HIGHLIGHT}$(python -c "import ansible; print(ansible.__version__)")${NORMAL}"

  # provision resources (future: skip running if already provisioned)
  set -x
  ( infrared openstack --topology-nodes=tester:1 \
      --topology-network=3_nets \
      --image=rhel-7.4-server-x86_64-updated \
      ${IR_CLOUD:-} \
      --prefix=$PREFIX \
      ${IR_DNS:-} \
      --key-file=${KEY} \
      > ${DIR}/provision.log || {
          rv=$?
          >&2 tail -n200 ${DIR}/provision.log
          exit $rv
        }
      ) 2>&1 | tee ${DIR}/provision.log

  infrared workspace node-list

  infrared octario --t=${COMPONENT_TESTER} --dir=${COMPONENT_PATH}

  if [ "${DISABLE_CLEANUP:-false}" != "true" ]; then
      infrared openstack ${IR_CLOUD:-} --image='fake_image' --prefix=$PREFIX --cleanup=yes > ${DIR}/cleanup.log
  fi

popd
