<pre>
==============================================================================
                      _      _             ______       ______
                     | \    | |           /  ____|     /  ____|   
                     | |\\  | |    __    |  /         |  /   
                     | | \\ | |  /    \  | |          | |    ___   
                     | |  \\| | |  ()  | |  \____     |  \___| |
                     |_|    \_|  \ __ /   \______|     \______/
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
