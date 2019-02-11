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

### Hierarchy:
- Network
    - NetworkInterface
    - Router
      - InputUnit
      - VirtualChannelArbitrator
      - RoutingUnit
      - Xbar*
      - SwitchUnit

(*)Note: diffused inside RoutingUnit and XbarArbitrator

### parameter:

- Network (#routers, topology, routing, switching, ...)
    - Router (flit_size, #buffers, buffer_size, ...)
