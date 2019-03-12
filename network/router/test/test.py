#!/usr/bin/python

#=========================================================================
# test.py
#=========================================================================
# This file starts the pytest for a RTL module and makes it easiler to 
# pass the configurations/arguments.
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 4, 2019

import pytest

import sys
import re

if __name__ == '__main__':
  args_pytest = [sys.argv[1], '--tb=short', '--capture=no']
  pytest.main(args_pytest)
