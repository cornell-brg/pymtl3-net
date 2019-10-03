"""
========================================================================
setup.py
========================================================================
setup.py inspired by the PyPA sample project:
https://github.com/pypa/sampleproject/blob/master/setup.py
"""

from os import path
from subprocess import check_output

from setuptools import find_packages, setup

#-------------------------------------------------------------------------
# get_version
#-------------------------------------------------------------------------

def get_version():
  # Check Python version compatibility
  import sys
  assert sys.version_info[0] > 2, "Python 2 is no longer supported!"

  result = "?"
  with open("ocn_pclib/__init__.py") as f:
    for line in f:
      if line.startswith("__version__"):
        _, result, _ = line.split('"')
  return result

#-------------------------------------------------------------------------
# get_long_descrption
#-------------------------------------------------------------------------

def get_long_description():
  here = path.abspath(path.dirname(__file__))
  with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    return f.read()

#-------------------------------------------------------------------------
# setup
#-------------------------------------------------------------------------

setup(

  name             = 'pymtl3-net',
  version          = get_version(),
  description      = 'PyMTL3-Net: an open-source Python-based framework for modeling, testing, and evaluating on-chip interconnection networks',
  long_description = get_long_description(),
  long_description_content_type="text/markdown",
  url              = 'https://github.com/cornell-brg/pymtl3-net',
  author           = 'Batten Research Group',
  author_email     = 'brg-pymtl@csl.cornell.edu',

  # BSD 3-Clause License:
  # - http://choosealicense.com/licenses/bsd-3-clause
  # - http://opensource.org/licenses/BSD-3-Clause

  license='BSD',

  # Pip will block installation on unsupported versions of Python
  python_requires=">=3.6",

  # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
  classifiers=[
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3 :: Only',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
  ],

  packages = find_packages(),

  scripts = [ 'script/pymtl3-net' ],

  install_requires = [
    'pymtl3',
    'ruamel.yaml'
  ],

)
