# Copyright (c) 2019 Cornell University
# All rights reserved.
#

def define_options():

    option("--network-topology", default="mesh", help="check configs/topologies for complete set")
    option("--network-rows", default=1, help="the number of rows in the mesh/torus topology")
    option("--link-width", default=128, help="width in bits for all links")
    option("--virtual-channels", default=1, help="number of virtual channels")
    option("--routing-algorithm", default="dor", help="dor: Dimention-ordered routing;
						       1turn:...")
