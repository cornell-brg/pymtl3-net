<pre>
==============================================================================
     __        ___     ___                          _             
  /\ \ \___   / __\   / _ \___ _ __   ___ _ __ __ _| |_ ___  _ __ 
 /  \/ / _ \ / /     / /_\/ _ | '_ \ / _ | '__/ _` | __/ _ \| '__|
/ /\  | (_) / /___  / /_\|  __| | | |  __| | | (_| | || (_) | |   
\_\ \/ \___/\____/  \____/\___|_| |_|\___|_|  \__,_|\__\___/|_|   
                                                                  
==============================================================================
</pre>
NoC Generator

### NoC generator hierarchy:
<img src="https://github.com/cornell-brg/wiki/blob/master/members/ct535/notes/hierarchy.png" width="400">
(*)Note: diffused inside RoutingUnit and XbarArbitrator

### test a set of simple tests.
![test table](https://github.com/cornell-brg/wiki/blob/master/members/ct535/notes/test.png)


### parameter:

- Network (#routers, topology, routing, switching, ...)
    - Router (flit_size, #buffers, buffer_size, ...)
