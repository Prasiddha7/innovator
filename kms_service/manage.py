#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks.

    Default to the local settings so that containers coming up for
    development work with DEBUG=True and permissive hosts.  An external
    DJANGO_SETTINGS_MODULE environment variable can still override this
    behaviour for production deployments.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kms_service.settings.local')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
