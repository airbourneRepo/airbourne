#!/usr/bin/python

"""Airbourne_Client"""

import sys
import json
import socket
import threading
from threading import *
from socket import *

#eigene Module
from lib import *
from rfc import *


if __name__ == '__main__':
	
	if(len(sys.argv) < 2):
		sys.exit(0)
	#IP wird dann hart reinprogrammiert
 
	while True:
		connectToServer(sys.argv[1])#address of ssh-reverse proxy
		initConnection()

else:
	logHandler("INFO", "Something tried to import airbourne.py as module")


