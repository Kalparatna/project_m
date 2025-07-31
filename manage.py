#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
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



'''
 these are all cosidering above given also , now give css file for team.css as theme mathcing to te navbar , consider color combination mathcing with  ,     don;t chnage navbard styling only other and for that only color , and if anything neceesary , 
as i provided,    give best color combinations shoould look like animated animated full of animations and 3D styling and all thing , making advanced styled   ,   make cartoon themed with animations and colors 

'''

#  background: linear-gradient(135deg, #01050e, #4847e2);