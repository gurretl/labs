#!/bin/bash

# Lionel Gurret
# 28 Nov 2020
echo "[1] Let's build our first image !"
sleep 2
docker image build -t gurretl/myfirstimage:v1 .
sleep 2

echo "[2] Our image is built, let's display it :"
sleep 2
docker image ls|grep gurretl
sleep 5

echo "[3] List image layers : "
sleep 2
docker image history gurretl/myfirstimage:v1
sleep 5

echo "[4] Let's a run container for testing"
sleep 2
docker container run -itd --name=testimage -p 8080:80 gurretl/myfirstimage:v1

echo "[5] Testing :"
sleep 2
docker container ls -l
sleep 3
curl http://localhost:8080 -s


