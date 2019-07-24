<pre>
=======================================
    ____        ____  _______   __
   / __ \__  __/ __ \/ ____/ | / /
  / /_/ / / / / / / / /   /  |/ / 
 / ____/ /_/ / /_/ / /___/ /|  /  
/_/    \__, /\____/\____/_/ |_/   
      /____/                      
=======================================
</pre>
[![Build Status](https://travis-ci.com/cornell-brg/posh-ocn.svg?branch=master)](https://travis-ci.com/cornell-brg/posh-ocn)

PyOCN (PyMTL-OCN Generator) is a parameterizable and powerful OCN (on-chip network) generator to generate synthesizable Verilog for different OCNs based on user-specified configurations (e.g., network size, topology, number of virtual channels, routing strategy, switching arbitration, etc.). It comes with PyMTL implementation and is the first one to provide functional-level (FL), cycle-level (CL), and register-transfer-level (RTL) modeling for building OCNs. Furthermore, POSH OCN Generator is open-source with a modular design and standardized interfaces between modules. The configurability and extensibility are maximized by its parametrization system to fit in various research and industrial needs.

Tutorial
--------------------------------------------------------

If you are interested in learning more about the PyOCN framework, we recommend you take a look at...


Related publications
--------------------------------------------------------------------------

- Shunning Jiang, Christopher Torng, and Christopher Batten. _"An Open-Source Python-Based Hardware Generation, Simulation, and Verification Framework."_ First Workshop on Open-Source EDA Technology (WOSET'18) held in conjunction with ICCAD-37, Nov. 2018.

- Shunning Jiang, Berkin Ilbeyi, and Christopher Batten. _"Mamba: Closing the Performance Gap in Productive Hardware Development Frameworks."_ 55th ACM/IEEE Design Automation Conf. (DAC-55), June 2018. 


License
--------------------------------------------------------------------------

PyOCN is offered under the terms of the Open Source Initiative BSD
3-Clause License. More information about this license can be found here:

  - http://choosealicense.com/licenses/bsd-3-clause
  - http://opensource.org/licenses/BSD-3-Clause


Installation
--------------------------------------------------------

PyOCN is developed based on PyMTL3 framework. More information about installation of PyMTL3 can be found here:
  - https://github.com/cornell-brg/pymtl3
  
PyOCN requires Python3.7 and has the following additional prerequisites:

 - verilator, pkg-config
 - git, Python headers, and libffi
 - virtualenv

The steps for installing these prerequisites and PyOCN on a fresh Ubuntu
distribution are shown below. They have been tested with Ubuntu Trusty
14.04.
...

Quickview
--------------------------------------------------------

### OCN generator hierarchy:
<img src="docs/code_hierarchy.png" width="400">

### Test with a set of simple tests:
![test table](docs/test.png)

### OCN generator design flow:
<img src="docs/design_flow.png" width="500">
 
### Generic network architecture:
<img src="docs/noc_structure.png" width="400">
 
### OCN generic router architecture:
<img src="docs/router_structure.png" width="400">

