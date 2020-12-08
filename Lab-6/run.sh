#!/bin/bash

# Lionel Gurret
# 28 Nov 2020
echo "[1] Let's run a container with an health check !"
sleep 2
docker run --name=nginx-proxy -d --health-cmd='stat /etc/nginx/nginx.conf || exit 1' nginx:1.13
while [ $(/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy) == "starting" ]
do
  echo "In until"
  sleep 1;
done
echo "Out until"
/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy
echo "AA"
exit

echo "[2] Is our container Healthy ?"
sleep 2
/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy
sleep 5

echo "[3] Let's make our container Unhealthy (remove nginx.conf)"
sleep 2
docker exec nginx-proxy rm /etc/nginx/nginx.conf
sleep 5

echo "[4] Is our container Healhty ?"
sleep 2
/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy
sleep 3
echo "[6] Fixing issue (create nginx.conf)"
sleep 2
docker exec nginx-proxy touch /etc/nginx/nginx.conf
sleep 3
/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy

