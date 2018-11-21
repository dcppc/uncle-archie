from setuptools import setup

"""
setup.py for Uncle Archie

Continuous integration (CI) testing tool for DCPPC.
"""

with open('requirements.txt') as f:
    required = [x for x in f.read().splitlines() if not x.startswith("#")]

# Note: the _program variable is set in __init__.py.
# it determines the name of the package/final command line tool.
from src import __version__

config = {
    'name': 'archie',
    'description': 'Uncle Archie is a home-brewed continuous integration server',
    'url': 'https://pages.charlesreid1.com/uncle-archie',
    'author': 'Charles Reid',
    'version' : __version__,
    'install_requires': required,
    'include_package_data' : True,
    'test_suite': 'tests',
    'tests_require': ['pytest'],
    'packages': [
        'archie',
        'archie.webapp',
        'archie.payload_handlers',
        'archie.tasks',
        'archie.tests',
    ],
    'package_dir' : {
        'archie' :                 'src',
        'archie.webapp' :          'src/webapp',
        'archie.payload_handlers': 'src/payload_handlers',
        'archie.tasks'  :          'src/tasks',
        'archie.tests'  :          'src/tests',
    },
    'scripts': [],
    'zip_safe' : False
}

setup(**config)
