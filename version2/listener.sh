#!/bin/bash
# Test connectivity to MaxScale's CDC port.

HOST=maxscale1
PORT=4001
ATTEMPTS=20

echo "Pinging MaxScale at $HOST to check network connectivity..."
ping -c 4 $HOST

echo "Attempting to connect to MaxScale's CDC port at $HOST:$PORT..."
count=0
while [ $count -lt $ATTEMPTS ]; do
    echo "Attempt $((count+1)) of $ATTEMPTS: Connecting to MaxScale CDC at $HOST:$PORT..."
    nc $HOST $PORT || echo "nc command failed, ensure nc is installed and $HOST is accessible"
    echo "Connection attempt finished. Retrying in 5 seconds..."
    sleep 5
    ((count++))
done
