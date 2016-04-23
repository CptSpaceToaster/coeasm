"""Package for coeasm"""
# System
import sys

__project__ = 'Coeasm'
__version__ = '1.1.1'

CLI = 'coeasm'
MAIN = 'coeasm.main:main'
VERSION = '{0} v{1}'.format(__project__, __version__)
DESCRIPTION = 'Assembler to .coe for an example instruction set'

MIN_PYTHON_VERSION = 3, 4

if not sys.version_info >= MIN_PYTHON_VERSION:
    exit("Python {}.{}+ is required.".format(*MIN_PYTHON_VERSION))
