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
while [ "$(kubectl get pods -n jenkins -l=app='jenkins' -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
   sleep 5
   echo "Waiting for Jenkins to be ready."
done
echo "[3] Install K9S"
# Install k9s
(cd && wget https://github.com/derailed/k9s/releases/download/v0.23.10/k9s_Linux_x86_64.tar.gz)
(cd && tar -xzf k9s_Linux_x86_64.tar.gz)
(cd && mv k9s /usr/local/bin/k9s)
sleep 2
echo "[4] Install Maven on Pod"
JENKINS_POD=$(kubectl get pods -n jenkins|grep jenkins|awk -F ' ' {'print $1'})
kubectl -n jenkins exec $JENKINS_POD -- apt update -y
kubectl -n jenkins exec $JENKINS_POD -- apt install maven -y
sleep 2
echo "[5] Get Jenkins password"
JENKINS_PWD=$(kubectl logs $JENKINS_POD --namespace jenkins|grep "Please use " -A3|grep -v "Please"|grep -v '^$')
sleep 2
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "URL : $url_first-31000-$url_second"
echo "Password : $JENKINS_PWD"
