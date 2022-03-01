#!/usr/bin/env python3

# Standard Library
import sys

# Django
from django.core.management import execute_from_command_line

# wger
from wger.tasks import (
    get_path,
    setup_django_environment,
)

import debugpy
import os

# optionally check to see what env you're running in, you probably only want this for 
# local development, for example: if os.getenv("MY_ENV") == "dev":

# RUN_MAIN envvar is set by the reloader to indicate that this is the 
# actual thread running Django. This code is in the parent process and
# initializes the debugger
if not os.getenv("RUN_MAIN"):
    debugpy.listen(("0.0.0.0", 9999))
    sys.stdout.write("Start the VS Code debugger now, waiting...\n")
    debugpy.wait_for_client()
    sys.stdout.write("Debugger attached, starting server...\n")

if __name__ == "__main__":

    # If user passed the settings flag ignore the default wger settings
    if not any('--settings' in s for s in sys.argv):
        setup_django_environment(get_path('settings.py'))

    # Alternative to above
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    execute_from_command_line(sys.argv)
