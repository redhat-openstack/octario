import argparse

import version

def get_version():
    """Returns program version."""

    return "Octario CLI version: %s" % \
            version.version_info.version_string()

def create_parser():
    """Create argument parser."""

    parser = argparse.ArgumentParser(
        description='Run Ansible component testing roles')

    parser.add_argument(
        '--component', dest='component', help='name of the component')
    parser.add_argument(
        '--rhos-releae', dest='rhos_release', help='rhos release')
    parser.add_argument(
        '--version', dest='version', action='version', version=get_version(),
        help='show version')

    return parser

def main():
    """Main function where the execution starts."""
    
    parser = create_parser()
    args = parser.parse_args()

if __name__ == '__main__':
    main()
