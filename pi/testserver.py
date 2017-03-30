#!/usr/bin/python

"""test server um Packete anzu nehmen"""
import socket
import sys
import json
import time

from rfc import *

def connect():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('', 1337))
	sock.listen(1)
	connection, client_address = sock.accept()
	return connection

connection = connect()

while True:

	#time.sleep(30)

	data = connection.recv(1024)
	jsonString = createResponse()
	connection.sendall(jsonString)
	time.sleep(3)

	#jsonString = createMonitore("start")
	#connection.sendall(jsonString)
	
	#time.sleep(3)

	#jsonString = createDump("start", 0)
	#connection.sendall(jsonString)
	#time.sleep(12)

	#jsonString = createDump("stop", 0)
	#connection.sendall(jsonString)
	#time.sleep(3)

	#jsonString = createDump("start" , 6)
	#connection.sendall(jsonString)

	time.sleep(110)

	#jsonString = createDeauth("C4:27:95:77:05:D3","78:F8:82:ED:A7:71",21)
	#connection.sendall(jsonString)

	#time.sleep(20)

	#jsonString = createDump("stop", 0)
	#connection.sendall(jsonString)

	time.sleep(3)


	#jsonString = createMonitore("stop")
	#connection.sendall(jsonString)
	#time.sleep(3)

	


connection.close()







