<pre>
==============================================================================
   ___  ___     __     ___                          _             
  /___\/ __\ /\ \ \   / _ \___ _ __   ___ _ __ __ _| |_ ___  _ __ 
 //  // /   /  \/ /  / /_\/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
/ \_// /___/ /\  /  / /_\\  __/ | | |  __/ | | (_| | || (_) | |   
\___/\____/\_\ \/   \____/\___|_| |_|\___|_|  \__,_|\__\___/|_|   
                                                                  
==============================================================================
</pre>

Posh OCN Generator is a parameterizable and powerful OCN generator to generate sythesizable Verilog for different OCNs based on user-specified configurations (e.g., network size, topology, number of virtual channels, routing strategy, switching arbitration, etc.). It comes with PyMTL implementation and is the first one to provide OCN simulation in functional-level (FL), cycle-level (CL), and register-transfer-level (RTL) modeling. Furthermore, Posh OCN Generator is open-source with a modular design and standardized interfaces between modules. The configurability and extensibility of XXX is maximized by its parametrization system to fit in various research and industrial needs.

### OCN generator hierarchy:
<img src="https://github.com/cornell-brg/wiki/blob/master/members/ct535/notes/code_hierarchy.png" width="400">

### Test with a set of simple tests:
![test table](https://github.com/cornell-brg/wiki/blob/master/members/ct535/notes/test.png)

### OCN generator design flow:
<img src="https://github.com/cornell-brg/wiki/blob/master/members/ct535/notes/design_flow.png" width="500">
 
### Generic network architecture:
<img src="https://github.com/cornell-brg/wiki/blob/master/members/ct535/notes/noc_structure.png" width="400">
 
### OCN generic router architecture:
<img src="https://github.com/cornell-brg/wiki/blob/master/members/ct535/notes/router_structure.png" width="400">

