#!/bin/bash

# Lionel Gurret
# 09 Mar 2021
echo "[1] Let's create our images"
sleep 2
docker build -t basic ./basic/.
docker build -t multistage ./multistage/.
docker build -t distroless-multistage ./distroless-multistage/.
docker build -t alpine-multistage ./alpine-multistage/.
sleep 2
echo "**************** RESULT *******************"
echo ""
echo "[2] Now we can display them :"
sleep 2
docker images



