#!/bin/bash
# Lionel Gurret
# 10th Dec 2020

# Ask for Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)
echo "Please provie Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)"
read -p "You can get it by clicking on + / Select port to view on Host 1: " answer
echo "Answer : $answer"

mkdir /mnt/data

url_first=$(echo $answer|awk -F '-' {'print $1'})
url_second=$(echo $answer|awk -F '-' {'print $2'})

echo "[1] Create Jenkins Namespace"
sleep 2
kubectl create ns jenkins
echo "[2] Deploy Jenkins"
sleep 2
kubectl apply -f .
sleep 20
echo "[3] Get Jenkins password"
JENKINS_POD=$(kubectl get pods -n jenkins|grep jenkins|awk -F ' ' {'print $1'})
JENKINS_PWD=$(kubectl logs $JENKINS_POD --namespace jenkins|grep "Please use " -A3|grep -v "Please"|grep -v '^$')
sleep 2
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "URL : $url_first-31000-$url_second"
echo "Password : $JENKINS_PWD"
