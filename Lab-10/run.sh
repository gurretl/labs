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

# Create a namespace for our registry
kubectl create ns jenkins

# Set JENKINS HTTPS Default Port
PORT_JENKINS=32577
JENKINS_URL=$url_first-$PORT_JENKINS-$url_second


exit

while [ "$(kubectl get pods -n registry -l=app='jenkins' -o jsonpath='{.items[*].status.containerStatuses[0].ready}'|grep false)" != "" ]; do
   sleep 5
   echo "Waiting for Jenkins to be ready."
done


# Display all information
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "You can logon Jenkins through this url : $JENKINS_URL"
echo ""
echo "User : admin"
echo "Default Password : P4ssw0rd!"
echo ""