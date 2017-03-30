#!/bin/bash

start_wlan1() {
	if ifconfig wlxc4e9840d9cfa; then 
		airmon-ng start wlxc4e9840d9cfa 
		exit 0
	fi
}

stop_wlan1() {
	if airmon-ng stop wlxc4e9840d9cfa; then
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
	if ifconfig wlxc4e9840d9cfa up; then 
		start_wlan1 
		exit 0
	else
		exit 1 
	fi
fi






