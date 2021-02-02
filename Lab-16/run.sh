#!/bin/bash

# Lionel Gurret
# 02 Fev 2021
echo "[1] Let's create our data directory"
sleep 2
mkdir /data
sleep 2

echo "[2] Now we can deploy our applicatoin :"
sleep 2
docker-compose up -d
sleep 5

echo "You can now connect to the 9191 port to display PowerDNS"
echo "Please create an admin user."
echo ""
echo "Configure API with the following :"
echo "API URL : http://pdns-master:8081/"
echo "Password: changeme"

