#!/bin/bash

# Setting terminal to use UTF-8 encoding
export LANG=C.UTF-8

width=$(tput cols)

if [ -z "$width"] || [ $width -le 0 ]; then
	width=80
fi

clear

colors=("32" "33" "34" "35" "36" "91" "92" "93" "94" "95" "96")

#infinite loop
while true; do
	# Choose random color
	color=${colors[$RANDOM % ${#colors[@]}]}

	# random position
	xpos=$((RANDOM % width))

	#Generate a random character
	text="$(tr -dc 'A-Za-z0-9!@#$%^&*()_+'</dev/urandom | head -c $((RANDOM % 5 + 3)))"

	# Print random characters at random positions
	printf "\e[${color}m%${xpos}s%s\e[0m\n" "" "$text"

	# delay 
	sleep 0.1
done