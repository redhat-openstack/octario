# Copyright 2018 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script comments all deps and install_command lines in a tox.ini file
# given by argument, f.e.:
#   $ ./comment_deps.py ./tox.ini

from shutil import copyfile
import sys

if sys.version_info.major == 3:
    import configparser as configparser
else:
    import ConfigParser as configparser

if __name__ == '__main__':
    copyfile(sys.argv[1], sys.argv[1] + '.orig')
    cp = configparser.ConfigParser()
    cp.read(sys.argv[1] + '.orig')

    for sec in cp.sections():
        for opt in cp.options(sec):
            if opt == 'deps' or opt == 'install_command':
                value = cp.get(sec, opt)
                # if the string is multiline, make it singleline
                value = value.replace('\n', ' ')
                # remove the uncommented option
                # and set it back as commented one
                cp.remove_option(sec, opt)
                cp.set(sec, "# " + opt, value)
    with open(sys.argv[1], 'w') as configfile:
        cp.write(configfile)
