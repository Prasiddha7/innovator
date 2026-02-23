#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks.

    By default we point to the *local* settings module so that when the
    container is started without any extra environment configuration it
    will use `settings.local` (DEBUG on, ALLOWED_HOSTS="*").  In production
    you can still override this by setting the standard
    DJANGO_SETTINGS_MODULE environment variable externally.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings.local')
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
