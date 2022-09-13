import sys
import os


sys.path.append(os.path.abspath("./../src"))

from lcli import __version__


print(__version__)
