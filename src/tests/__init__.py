import os
import sys


def load_local_packages_from_src():
    sys.path.append(os.path.abspath("./../src"))


load_local_packages_from_src()
