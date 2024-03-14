#!/bin/bash
# listener.sh: A simple script to listen to MaxScale's CDC port.

# MaxScale CDC service port and host
PORT=4001
HOST=maxscale1

# Using netcat to listen for data from MaxScale
nc $HOST $PORT
