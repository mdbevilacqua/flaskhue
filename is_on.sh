#!/bin/bash

. ./hueconf

curl="curl -s -X GET http://${hue_host}/api/${hue_key}"
total_lights=`${curl}/lights | jq '. | length'`

echo -en "\e[38;5;26m:::Light Status:::\e[0m"
echo ""

for (( i=1; i<$total_lights; i++ ));
    do  
        		name=`${curl}/lights/${i} | jq -r '.name?'`
		        on=`${curl}/lights/${i} | jq -r '.state?.on?'`

				if [[ -z "$name" ]];
					then
						echo "${i}: Light not found on bridge"
					else
						echo "${i}: ${name} ${on} "
				fi
done
