#!/bin/bash

function check_okay {
	if [ $? -ne 0 ]
	then
		echo
		pwd
		echo "FAILED"
		echo
		exit 1
	fi
}

cd make
make
check_okay
cd ..
mkdir -p LOGS
