#!/usr/bin/env python

"""show-attitude.py: Script to ask the MultiWii Board attitude and print it."""

__author__ = "Aldo Vargas"
__copyright__ = "Copyright 2017 Altax.net"

__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "Aldo Vargas"
__email__ = "alduxvm@gmail.com"
__status__ = "Development"

from pymultiwii import MultiWii
from sys import stdout
import time

if __name__ == "__main__":

    board = MultiWii("/dev/ttyACM0")
    #board = MultiWii("/dev/tty.SLAB_USBtoUART")
    try:
        while True:
            #board.getData(MultiWii.RAW_GPS)
            #print(board.rawGPS)
            print(board.getData(MultiWii.WP)) #uncomment for regular printing

            # Fancy printing (might not work on windows...)
            #message = "angx = {:+.2f} \t angy = {:+.2f} \t heading = {:+.2f} \t elapsed = {:+.4f} \t".format(float(board.attitude['angx']),float(board.attitude['angy']),float(board.attitude['heading']),float(board.attitude['elapsed']))
            #stdout.write("\r%s" % message )
            #stdout.flush()
            # End of fancy printing
    except:
        print ("Error on Main: "+str(error))
