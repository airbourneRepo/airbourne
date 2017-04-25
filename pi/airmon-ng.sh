#!/bin/bash

start_wlan1() {
	if ifconfig wlan0; then 
		airmon-ng start wlan0 
		exit 0
	fi
}

stop_wlan1() {
	if airmon-ng stop wlan0; then
		iw dev mon0 del
		exit 0
	else
		exit 1
	fi
}

if [ $# -eq 1 ]; then 
	if [ "$1" == "stop" ]; then 
		stop_wlan1 
		exit 0
	else
		exit 1
	fi
fi

if ! start_wlan1; then 
	if ifconfig wlan0 up; then 
		start_wlan1 
		exit 0
	else
		exit 1 
	fi
fi






