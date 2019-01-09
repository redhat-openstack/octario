# Global and component specific scripts

## Global Scripts

In order to deploy scripts with Octario, no matter what component is used,
put the script in octario/roles/setup_environment/files directory.

## Component Specific Scripts

If your script is not intended to be used by all components and is only relevant
to your component then place it in the octario/components_config/<version>/<component_name>/scripts
directory.


In both global and component-specific options, Octario will automatically copy the
script during the run to /tmp on the remote host.
