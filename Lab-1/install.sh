#!/bin/bash

# Lionel Gurret
# 18th Nov 2020

# Install Helm 3.4.1
(cd && wget https://get.helm.sh/helm-v3.4.1-linux-amd64.tar.gz)
(cd && tar -zxvf helm-v3.4.1-linux-amd64.tar.gz)
(cd && mv linux-amd64/helm /usr/local/bin/helm)
# Install k9s
(cd && wget https://github.com/derailed/k9s/releases/download/v0.23.10/k9s_Linux_x86_64.tar.gz)
(cd && tar -xzf k9s_Linux_x86_64.tar.gz)
(mv && k9s /usr/local/bin/k9s)

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

# Create a namespace for our stacs
kubectl create ns metrics

# Install (or upgrade) Prometheus / Grafana Stack (adapt file if you use custom files)
helm upgrade --install prometheus -f prometheus.yml -n metrics prometheus-community/prometheus
helm upgrade --install grafana -f grafana.yml -n metrics grafana/grafana

# Expose services to reach them externally
kubectl expose service prometheus-server --type=NodePort --target-port=9090 --name=prometheus-server-np -n metrics
kubectl expose service grafana --type=NodePort --target-port=3000 --name=grafana-np -n metrics

# Display end of script
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"

# Get Grafana Endpoint
PORT_GRAF=$(kubectl -n metrics get service grafana-np -o yaml|grep nodePort|awk -F ': ' {'print $2'})
PORT_PROM=$(kubectl -n metrics get service prometheus-server-np -o yaml|grep nodePort|awk -F ': ' {'print $2'})

echo "You can logon Prometheus Web Interface through this port : $PORT_PROM"

# kubectl -n metrics get services -o yaml|grep -i nodePort:
# Display secret to use 
echo "You can login Grafana using admin user and the following password (port $PORT_GRAF):"
kubectl get secret --namespace metrics grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

