Pymtl3-net is an open-source Python-based framework for modeling, testing,
and evaluating on-chip interconnection networks.

Please follow the steps to go through the demo:

[step 0] Make sure you are NOT logged in to repl.

[step 1] Edit the YAML.

[step 2] Click run.

[step 3] Look at the console output and generated Verilog.

[step 4] Download zip of the project to use the Verilog and view the VCD.

==========================================================================

Additional notes:

0. [do not log in repl]
log in to repl will lead to repl crash when generating Verilog file.

1. [edit config.yml]
Editing any file will automatically fork the project as an anonymous user.
The configurations are written in the YAML file (i.e., config.yml) and
easily to be changed.

2. [run main.py]
In this demo, we can simply run the main.py to generate synthesizable
Verilog, verify the target OCN (on-chip network) model, simulate it with
single packet, and simulate it with different traffic patterns.

3. [check NetworkRTL.sv]
By enabling the action of 'generate' in config.yml, a synthesizable RTL
can be generated for the target OCN model.

4. [verify network model]
By enabling the action of 'verify' in config.yml, the target OCN model
will be verified by a set of test cases.

5. [check dumped VCD]
By enabling the action of 'simulate-1pkt' in config.yml, the line trace at
each cycle will be printed out. Meanwhile, the corresponding VCD file will
be dumped, which can be downloaded and viewed using gtkwave.

6. [check latency vs. bandwidth]
By enabling the action of 'simulate-lat-vs-bw' in config.yml, the target
OCN model will be simulated with specific traffic pattern(s) across
different injection rates.


