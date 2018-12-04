#!/usr/bin/env bash
rm response.bin
for i in `sed 's/ //g;' request.txt`; do
	echo "Sent: $i"
	echo -n "$i" | xxd -r -p | nc 127.0.0.1 $PORT >> response.bin
	read a
done