#=========================================================================
# InputUnitRTL_test.py
#=========================================================================
# Unit tests for InputUnitRTL.
# 
# Author : Yanghui Ou, Cheng Tan
#   date : Feb 14, 2019

from pymtl import *
import router
from router.InputUnitRTL import InputUnitRTL

def test_compile():
  _ = InputUnitRTL( num_entries=1, pkt_type=Bits32 ) 
