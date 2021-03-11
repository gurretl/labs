#!/bin/bash

# Lionel Gurret
# 11 Mar 2021
echo "[1] Let's generate our docker-compose file"
sleep 2
sleep 2
cat main.yml | docker run --rm -i brettmc/docker-compose-generator generate -e IMAGE="redis:alpine" -e MYSQL_ROOT_PASSWORD="somewordpress" -e MYSQL_DATABASE="wordpress" -e MYSQL_USER="wordpress" -e MYSL_PASSWORD="wordpress" -e WORDPRESS_DB_HOST="db:3306" -e WORDPRESS_DB_USER="wordpress" -e WORDPRESS_DB_PASSWORD="wordpress" -e WORDPRESS_DB_NAME="wordpress" > output.yml
echo "**************** RESULT *******************"
echo "Here is your docker-compose !"
echo ""
cat output.yml
sleep 2
