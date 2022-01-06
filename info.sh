#!/usr/bin/env bash

ssh ubuntu@192.168.100.21 ' \
	hostname ; \
	hostname -I | sed "s/ .*//" ; \
       	free -m | grep "^Mem" ; \
       	df -h | grep "mmcblk0p2 " ; \
       	sudo vcgencmd measure_temp' \
	>/tmp/out.file
