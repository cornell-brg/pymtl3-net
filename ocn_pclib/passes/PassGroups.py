"""
==========================================================================
PassGroups.py
==========================================================================

Author : Yanghui Ou
  Date : Aug 30, 2019

"""
from pymtl3.dsl import Component
from pymtl3.passes.CLLineTracePass import CLLineTracePass
from pymtl3.passes.DynamicSchedulePass import DynamicSchedulePass
from pymtl3.passes.GenDAGPass import GenDAGPass
from pymtl3.passes.LineTraceParamPass import LineTraceParamPass
from pymtl3.passes.mamba.HeuristicTopoPass import HeuristicTopoPass
from pymtl3.passes.mamba.TraceBreakingSchedTickPass import TraceBreakingSchedTickPass
from pymtl3.passes.mamba.UnrollTickPass import UnrollTickPass
from pymtl3.passes.OpenLoopCLPass import OpenLoopCLPass
from pymtl3.passes.SimpleSchedulePass import SimpleSchedulePass
from pymtl3.passes.SimpleTickPass import SimpleTickPass
from pymtl3.passes.WrapGreenletPass import WrapGreenletPass
from .VcdGenerationPass import VcdGenerationPass

SimulationPass = [
  GenDAGPass(),
  WrapGreenletPass(),
  DynamicSchedulePass(),
  CLLineTracePass(),
  VcdGenerationPass(),
  SimpleTickPass(),
  Component.lock_in_simulation
]


