FROM registry.access.redhat.com/rhel7/rhel

MAINTAINER Arie Bregman <abregman@redhat.com>

# Install tox, update image, and clear cache
RUN yum -y install python-tox && yum -y update; yum clean all

RUN echo "Testing Neutron OSP 13" > /var/lib/test_env

CMD ["/usr/bin/tox", "-e py27"]
