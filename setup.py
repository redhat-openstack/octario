#!/usr/bin/env python

# Copyright 2016 Red Hat, Inc.
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

from octario.lib.release import __AUTHOR__
from octario.lib.release import __VERSION__
from pip import req
from setuptools import find_packages
from setuptools import setup

import os
import platform

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = req.parse_requirements('requirements.txt', session=False)

# reqs is a list of requirement from requirements.txt
reqs = [str(octario.req) for octario in install_reqs]

with open("LICENSE") as file:
    license = file.read()
with open("README.md") as file:
    long_description = file.read()

setup(
    name='octario',
    version=__VERSION__,
    author=__AUTHOR__,
    author_email='rhos-qe-dept@redhat.com',
    long_description=long_description,
    license=license,
    install_requires=reqs,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['octario = octario.lib.cli:main']
    }
)

if all(platform.linux_distribution(supported_dists="redhat")):
    # For RedHat based systems, get selinux binding
    try:
        import selinux
    except ImportError as e:
        new_error = type(e)(e.message + ". check that 'libselinux-python is "
                                        "installed'")

        from distutils import sysconfig
        import shutil
        import sys

        if hasattr(sys, 'real_prefix'):
            # check for venv
            VENV_SITE = sysconfig.get_python_lib()

            SELINUX_PATH = os.path.join(
                sysconfig.get_python_lib(plat_specific=True,
                                         prefix=sys.real_prefix),
                "selinux")

            if not os.path.exists(SELINUX_PATH):
                raise new_error

            dest = os.path.join(VENV_SITE, "selinux")
            if os.path.exists(dest):
                raise new_error

            # filter precompiled files
            files = [os.path.join(SELINUX_PATH, f)
                     for f in os.listdir(SELINUX_PATH)
                     if not os.path.splitext(f)[1] in (".pyc", ".pyo")]

            # add extra file for (libselinux-python)
            _selinux_file = os.path.join(
                sysconfig.get_python_lib(plat_specific=True,
                                         prefix=sys.real_prefix),
                "_selinux.so")
            if os.path.exists(_selinux_file):
                shutil.copy(_selinux_file, os.path.dirname(dest))
                files.append(_selinux_file)

            os.makedirs(dest)
            for f in files:
                shutil.copy(f, dest)
        else:
            raise new_error
        import selinux  # noqa
