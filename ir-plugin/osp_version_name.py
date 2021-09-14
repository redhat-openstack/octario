#!/usr/bin/env python

# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import logging
import os$
import sys


def find_path(direntry):
    for root, dirs, files in os.walk(os.path.expanduser('~')):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for name in dirs:
            if name == direntry:
                return(os.path.abspath(os.path.join(root, name)))

sys.path.append(find_path('octario'))

from octario.lib.component import Component # noqa


LOG = logging.getLogger("OctarioLogger")
LOG.setLevel(logging.ERROR)


def main(component_path):
    cmpnt = Component(component_path)
    release = cmpnt.get_rhos_release()
    repo = cmpnt.get_rhos_release_repo()
    name = cmpnt.get_name()
    if release is not None and name is not None:
        json_out = {
            'plugin': 'iroctario',
            'name': name,
            'version': release,
            'repo': repo,
        }
        print(json.dumps(json_out))


if __name__ == "__main__":
    """Helper script used by InfraRed-Octario plugin to discover component
       name and OSP release number.
    """

    if len(sys.argv) != 2:
        LOG.error("Improper number of arguments, passed %d instead of 1" %
                  int(len(sys.argv) - 1))
        sys.exit(1)
    main(sys.argv[1])
