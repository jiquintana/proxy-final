#!/bin/sh
HOWMANY=$1
mkdir -p tmp
time ab -n 100000 -c 10 -g tmp/test_data_$HOWMANY.txt http://127.0.0.1:8002/ > tmp/timming.$HOWMANY
