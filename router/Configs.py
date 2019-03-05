#=========================================================================
# InputUnitRTL.py
#=========================================================================
# This file contains basic configurations for the network generator
# The detailed/internal configurations/parameters can be set in the code
# hierarchy via set_parameter().
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 4, 2019

import argparse

def configure_network(args):

  parser = argparse.ArgumentParser()

  parser.add_argument("--topology",         type=str, default="Crossbar",
                    choices=['Crossbar', 'Ring', 'Mesh', 'Torus'],
                    help="check Configs for complete set")

  parser.add_argument("--mesh-rows",        type=int, default=0,
                    help="the number of rows in the mesh topology")

  parser.add_argument("--router-latency",   type=int, default=1,
                    action="store",
                    help="indicating the number of pipeline stages in router.")

  parser.add_argument("--link-latency",     type=int, default=1, 
                    action="store",
                    help="indicating the number of input stages in router.")

  parser.add_argument("--link-width-bits",  type=int, default=128, 
                    action="store",
                    help="width in bits for all links inside garnet.")

  parser.add_argument("--virtual-channel",  type=int, default=4, 
                    action="store",
                    help="""number of virtual channels per virtual network
                          inside garnet network.""")

  parser.add_argument("--routing-strategy", type=str, default='DOR',
                    action="store", choices=['DOR', 'WFR', 'NLR'],
                    help="routing algorithm in network.")
#
  configs = parser.parse_args(args)
  return configs

if __name__ == "__main__": configure_network()

