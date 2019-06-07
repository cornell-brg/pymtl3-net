<pre>
==============================================================================
   ___  ___     __     ___                          _             
  /___\/ __\ /\ \ \   / _ \___ _ __   ___ _ __ __ _| |_ ___  _ __ 
 //  // /   /  \/ /  / /_\/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
/ \_// /___/ /\  /  / /_\\  __/ | | |  __/ | | (_| | || (_) | |   
\___/\____/\_\ \/   \____/\___|_| |_|\___|_|  \__,_|\__\___/|_|   
                                                                  
==============================================================================
</pre>

POSH OCN Generator is a parameterizable and powerful OCN (on-chip network) generator to generate sythesizable Verilog for different OCNs based on user-specified configurations (e.g., network size, topology, number of virtual channels, routing strategy, switching arbitration, etc.). It comes with PyMTL implementation and is the first one to provide functional-level (FL), cycle-level (CL), and register-transfer-level (RTL) modeling for building OCNs. Furthermore, POSH OCN Generator is open-source with a modular design and standardized interfaces between modules. The configurability and extensibility are maximized by its parametrization system to fit in various research and industrial needs.

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

