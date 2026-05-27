#!/bin/bash
# example is: curl -X POST http://$hue_host/api -d '{"devicetype":"mylaptop"}'
# CAUTION: I have not found a way to remove keys from the whitelist without clearing the bridge config. Use this with care!

echo "CAUTION: Install jq(1) first."
echo "CAUTION: I have not found a way to remove keys from the whitelist without clearing the bridge config. Use this with care!"
echo "CAUTION: Control-C if you need to stop now."

echo -n "Enter your device's host name as an ID (ie mylaptop, myFlaskVM, etc) and press [ENTER]: "
read dt

echo -n "Enter host or IP of the hue bridge and press [ENTER]: "
read hue_host

echo -n "Press the HUE link button now. Come back and press [ENTER]: "
read ready

if [ -z ${ready} ];
	then
	    result=`curl -s -X POST http://$hue_host/api -d '{"devicetype":"'$dt'"}'`
fi

echo ${result} | jq -r .
