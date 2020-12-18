#!/bin/bash

# Lionel Gurret
# 18th Dec 2020

# Ask for Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)
echo "Please provie Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)"
read -p "You can get it by clicking on + / Select port to view on Host 1: " answer
echo "Answer : $answer"

# Split URL to get 2 parts
url_first=$(echo $answer|awk -F '-' {'print $1'})
url_second=$(echo $answer|awk -F '-' {'print $2'})

# Install Helm 3.4.1
(cd && wget https://get.helm.sh/helm-v3.4.1-linux-amd64.tar.gz)
(cd && tar -zxvf helm-v3.4.1-linux-amd64.tar.gz)
(cd && mv linux-amd64/helm /usr/local/bin/helm)
# Install k9s
(cd && wget https://github.com/derailed/k9s/releases/download/v0.23.10/k9s_Linux_x86_64.tar.gz)
(cd && tar -xzf k9s_Linux_x86_64.tar.gz)
(cd && mv k9s /usr/local/bin/k9s)

# Install repo Harbor
helm repo add harbor https://helm.goharbor.io

# If you want to modify harbor configuration, uncomment this line and configure as you wish
# In this example, I have provided a default harbor.yml file for testing
(cd && helm inspect values harbor/harbor > custom_harbor.yml)

# Create a namespace for our registry
kubectl create ns registry

# Set Harbor HTTPS Default Port
PORT_HARBOR=30003

# With configure our helm values file
sed -i "s,HARBOR_URL,$url_first-$PORT_HARBOR-$url_second," harbor.yml

# Git delete to be sure nothing will be pushed
rm -rf ../.git

# Install (or upgrade) Harbor (adapt yml file if you use custom files)
helm upgrade --install harbor -f harbor.yml -n registry harbor/harbor

while [ "$(kubectl get pods -n registry -l=app='harbor' -o jsonpath='{.items[*].status.containerStatuses[0].ready}'|grep false)" != "" ]; do
   sleep 5
   echo "Waiting for Harbor to be ready."
done
# Display all information
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "You can logon Harbor through this url : $url_first-$PORT_HARBOR-$url_second"
echo ""
echo "User : admin"
echo "Default Password : Harbor12345"

