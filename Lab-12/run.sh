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

echo "[7] Replace JENKINS_URL_SANS_HTTPS in prometheus.yml"
sed -i "s,JENKINS_URL_SANS_HTTPS,$JENKINS_URL_SANS_HTTPS," prometheus.yml

echo "[8] Deploy Grafana and Prometheus"
# Install repo prometheus-community
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# If you want to modify prometheus configuration, uncomment this line and configure as you wish
# In this example, I have provided a default prometheus.yml file for testing
(cd && helm inspect values prometheus-community/prometheus > custom_prometheus.yml)

# Install repo grafana
helm repo add grafana https://grafana.github.io/helm-charts

# If you want to modify grafana configuration, uncomment this line and configure as you wish
# In this example, I have provided a grafana.yml values file for testing
(cd && helm inspect values grafana/grafana > custom_grafana.yml)

# Create a namespace for our stack
kubectl create ns metrics

# Install (or upgrade) Prometheus (adapt yml file if you use custom files)
helm upgrade --install prometheus -f prometheus.yml -n metrics prometheus-community/prometheus
# Expose service to reach them externally
kubectl expose service prometheus-server --type=NodePort --target-port=9090 --name=prometheus-server-np -n metrics

# Get Prometheus Endpoint
PORT_PROM=$(kubectl -n metrics get service prometheus-server-np -o yaml|grep nodePort|awk -F ': ' {'print $2'})

# With Prometheus port, we can configure grafana.yml
#$PROMETHEUS_URL="$url_first-$PORT_PROM-$url_second"
sed -i "s,PROMETHEUS_URL,$url_first-$PORT_PROM-$url_second," grafana.yml

# Install (or upgrade) Grafana  (adapt yml file if you use custom files)
helm upgrade --install grafana -f grafana.yml -n metrics grafana/grafana
# Expose service to reach them externally
kubectl expose service grafana --type=NodePort --target-port=3000 --name=grafana-np -n metrics

# Get Grafana Endpoint
PORT_GRAF=$(kubectl -n metrics get service grafana-np -o yaml|grep nodePort|awk -F ': ' {'print $2'})
GRAFANA_URL=$url_first-$PORT_GRAF-$url_second

while [ "$(kubectl get pods -n metrics -l=app.kubernetes.io/instance=grafana -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ];do
   sleep 5
   echo "Waiting for Grafana to be ready."
done

while [ "$(kubectl get pods -n jenkins -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
   sleep 5
   echo "Waiting for Jenkins to be ready..."
done

# Remove .git to avoid pushing modified files
rm -rf ../.git

# Display all information
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "You can logon Jenkins through this url : $JENKINS_URL"
echo ""
echo "User : admin"
echo "Default Password : P4ssw0rd!"
echo ""
echo "You can logon Prometheus Web Interface through this url : $url_first-$PORT_PROM-$url_second"
echo ""
echo "You can login Grafana using admin user and the following password (port $PORT_GRAF):"
echo "URL : $url_first-$PORT_GRAF-$url_second"
echo "User : admin"
echo "Password : $(kubectl get secret --namespace metrics grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo)"
echo ""
