#!/bin/bash

# The IP of the server to check for connection
SERVER=8.8.8.8

# Do some pinging
ping -c2 ${SERVER} > /dev/null

# If ping failed, restart wifi
if [ $? != 0 ]
then
	# Restart the wireless interface
	ifconfig wlan0 down
	ifconfig wlan0 up
fi
