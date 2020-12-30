#!/bin/bash
# Lionel Gurret
# 30th Dec 2020

# Ask for Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)
echo "Please provie Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)"
read -p "You can get it by clicking on + / Select port to view on Host 1: " answer
echo "Answer : $answer"

# Split URL to get 2 parts
url_first=$(echo $answer|awk -F '-' {'print $1'})
url_second=$(echo $answer|awk -F '-' {'print $2'})

# Install Helm 3.4.1
echo "[1] We install Helm"
sleep 2
(cd && wget https://get.helm.sh/helm-v3.4.1-linux-amd64.tar.gz)
(cd && tar -zxvf helm-v3.4.1-linux-amd64.tar.gz)
(cd && mv linux-amd64/helm /usr/local/bin/helm)

echo "[2] We install K9S"
sleep 2
# Install k9s
(cd && wget https://github.com/derailed/k9s/releases/download/v0.23.10/k9s_Linux_x86_64.tar.gz)
(cd && tar -xzf k9s_Linux_x86_64.tar.gz)
(cd && mv k9s /usr/local/bin/k9s)

# We will use our own local image to be able to manage and push our Jenkins plugins.txt list
echo "[3] We need to build our own local custom jenkins image"
sleep 2
docker build . -t lionel/jenkins:v1

# Create a namespace for our registry
echo "[4] Create Kube namespace jenkins"
sleep 2
kubectl create ns jenkins

# Set JENKINS HTTPS Default Port
PORT_JENKINS=31000
sed -i "s,PORT_JENKINS,$PORT_JENKINS," ./helm/jenkins-k8s/values.yaml
JENKINS_URL=$url_first-$PORT_JENKINS-$url_second
JENKINS_URL_SANS_HTTPS=$(echo $JENKINS_URL|awk -F '/' {'print $3'})

# helm install
echo "[5] Install Jenkins with helm"
sleep 2
helm upgrade --install jenkins ./helm/jenkins-k8s -n jenkins

echo "[6] Add dummy jobs to Jenkins"
# Waiting Jenkins Pods to be in ready state
echo "Waiting for Jenkins to be ready..."
sleep 2
while [ "$(kubectl get pods -n jenkins -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
   sleep 5
   echo "Waiting for Jenkins to be ready..."
done
#https://github.com/gangsta/jenkins-prometheus-grafana/tree/master/jenkins/jobs
JENKINS_POD=$(kubectl get pods -n jenkins -l=app='jenkins-k8s' -o jsonpath='{.items[*].metadata.name}')
kubectl cp jobs jenkins/$JENKINS_POD:/var/jenkins_home/ -c jenkins-k8s
sleep 2
echo "We restart Jenkins to apply new Job imported !!"
kubectl -n jenkins rollout restart deployment jenkins-jenkins-k8s
sleep 2

while [ "$(kubectl get pods -n jenkins -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
   sleep 5
   echo "Waiting for Jenkins to be ready..."
done

# Display all information
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "You can login Jenkins through this url : $JENKINS_URL"
echo "User : admin"
echo "Password : P4ssw0rd!"
echo ""
