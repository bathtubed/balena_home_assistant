#!/bin/bash

mkdir -p /data/media && mount /data/media
mkdir -p /data/backups && mount /data/backups

echo "Starting dlna and samba"

service minidlna start
service smbd start
while true
do
	sleep 1
done
