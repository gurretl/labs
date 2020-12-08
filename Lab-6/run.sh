#!/bin/bash
# Lionel Gurret
# 08 Dec 2020
echo "[1] Pull Image ngixn"
docker pull nginx:1.13
echo "[2] Let's run a container with an health check !"
sleep 2
docker run --name=nginx-proxy -d --health-cmd='stat /etc/nginx/nginx.conf || exit 1' nginx:1.13
while [ "`docker inspect -f {{.State.Health.Status}} nginx-proxy`" != "healthy" ]; do sleep 2; done
/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy
echo "[3] Is our container Healthy ?"
sleep 2
/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy
sleep 5
echo "[4] Let's make our container Unhealthy (remove nginx.conf)"
sleep 2
docker exec nginx-proxy rm /etc/nginx/nginx.conf
sleep 5
echo "[5] Is our container Healhty ?"
while [ "`docker inspect -f {{.State.Health.Status}} nginx-proxy`" != "unhealthy" ]; do sleep 2; done
/usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy
echo "[6] Fixing issue (create nginx.conf)"
sleep 2
docker exec nginx-proxy touch /etc/nginx/nginx.conf
sleep 3
echo "Please Run the following command and wait to see when your container is healthy again :"
echo "watch /usr/bin/docker inspect -f {{.State.Health.Status}} nginx-proxy"

