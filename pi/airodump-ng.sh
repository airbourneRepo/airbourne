#!/bin/bash

airodump_global() {
	if airodump-ng --write sendme --output-format csv mon0
	then
		exit 0
	else
		exit 1
	fi
}

airodump_channel() {
	if airodump-ng -c $1 --write sendme --output-format csv mon0 
	then
		exit 0
	else
		exit 1
	fi
}

if [ $# -eq 0 ]; then
	airodump_global
else
	airodump_channel $1
fi

		
	


