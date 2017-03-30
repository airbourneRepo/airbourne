#!/usr/bin/python

"""anything related to sockets and packets"""

import json
import netifaces
import sys
import threading
import socket

from netifaces import AF_INET
from threading import *

OK_MSG = 0
HELLO_MSG = 1
RESP_MSG = 2
MON_MSG = 3
DUMP_MSG = 4
HEAD_MSG = 5
DATA_MSG = 6
SHELL_MSG = 7
DEAUTH_MSG = 8
SNIFF_MSG = 9
ERROR_MSG = 255

START = "start"
STOP = "stop"
PORT = 1337


##############################
# Almost nothing to see here.#
##############################
def createHello():
	jsonString = { 
				'Type': HELLO_MSG,
	 			'SourceAddress' : netifaces.ifaddresses('enp4s0')[AF_INET][0]['addr'], #iface of PI
	} 
	return json.dumps(jsonString)#+'\0'

def createData(line):
	jsonString = {
		   		'Type' : DATA_MSG,
		   		'Data' : line,
	}
	return json.dumps(jsonString)#+'\0'

def createHead(line):
	jsonString = {
				'Type' : HEAD_MSG,
			   	'Data' : line,
	}
	return json.dumps(jsonString)#+'\0'



############################################################################
# Just used by server. Exists because of completeness and testing purposes.#
############################################################################
def createOK():
	jsonString = {
				'Type' : OK_MSG,
	}

def createResponse():
	jsonString = {
				'Type' : RESP_MSG,
				'SourceAddress' : '122.122.122.122',
	}
	return json.dumps(jsonString)#+'\0'

def createMonitore(command):
	jsonString = {
				'Type' : MON_MSG,
				'Command' : command,
	}
	return json.dumps(jsonString)#+'\0'

def createDump(command, channel):	
	jsonString = {
				'Type' : DUMP_MSG,
				'Command' : command,
				'Channel' : channel,
	}
	return json.dumps(jsonString)#+'\0'

def createDeauth(ap, victim, count):
	jsonString = {
				'Type' : DEAUTH_MSG,
				'Ap' : ap,
				'Victim' : victim,
				'Count' : count,
				
	}
	return json.dumps(jsonString)#+'\0'


