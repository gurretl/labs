#!/bin/bash

# Lionel Gurret
# 18th Nov 2020

# Ask for Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)
echo "Please provie Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)"
read -p "You can get it by clicking on + / Select port to view on Host 1: " answer
echo "Answer : $answer"

# Split URL to get 2 parts (Used in grafana.yml config to link prometheus)
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
$GRAFANA_URL="$url_first-$PORT_GRAF-$url_second"

# Remove .git directory to avoid pushing unwanted changes to GitHub
rm -rf ../.git

# Display all information
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "You can logon Prometheus Web Interface through this url : $url_first-$PORT_PROM-$url_second"
echo ""
echo "You can login Grafana using admin user and the following password (port $PORT_GRAF):"
echo "URL : $url_first-$PORT_GRAF-$url_second"
echo "User : admin"
echo "Password : $(kubectl get secret --namespace metrics grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo)"
echo ""
echo "!!!!!!"
echo "WARNING : PLEASE WAIT EVERYTHING IS UP BEFORE DEBUGGING (watch kubectl -n metrics get deployments/grafana)"
echo "!!!!!!"
echo ""
kubectl -n metrics get deployments/grafana
