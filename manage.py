#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""

    # If Website is hosted, use the production settings
    if os.environ.get("WEBSITE_HOSTNAME"):
        print("Production settings loaded")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendence_tracker.production")
    else:
        print("Loading environment variables for .env file")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendence_tracker.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
