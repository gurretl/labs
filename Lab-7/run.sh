#!/bin/bash
# Lionel Gurret
# 10th Dec 2020

# Ask for Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)
echo "Please provie Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)"
read -p "You can get it by clicking on + / Select port to view on Host 1: " answer
echo "Answer : $answer"

# Split URL to get 2 parts (Used in grafana.yml config to link prometheus)
url_first=$(echo $answer|awk -F '-' {'print $1'})
url_second=$(echo $answer|awk -F '-' {'print $2'})

# Install Helm 3.4.1
echo "[1] First, we need to install Helm :"
sleep 2
(cd && wget https://get.helm.sh/helm-v3.4.1-linux-amd64.tar.gz)
(cd && tar -zxvf helm-v3.4.1-linux-amd64.tar.gz)
(cd && mv linux-amd64/helm /usr/local/bin/helm)
echo "[2] We can also install k9s if we want to debug :"
sleep 2
# Install k9s
(cd && wget https://github.com/derailed/k9s/releases/download/v0.23.10/k9s_Linux_x86_64.tar.gz)
(cd && tar -xzf k9s_Linux_x86_64.tar.gz)
(cd && mv k9s /usr/local/bin/k9s)

# Add Repo bitname
echo "[3] We know install Kubeapps !"
sleep 2
helm repo add bitnami https://charts.bitnami.com/bitnami
kubectl create namespace kubeapps
helm install kubeapps --namespace kubeapps bitnami/kubeapps

echo "Waiting for pods to be up and running..."
sleep 10

# Create a demo credential with which to access Kubeapps and Kubernetes
echo "[4] We need to install Demo credentials"
kubectl create serviceaccount kubeapps-operator
kubectl create clusterrolebinding kubeapps-operator --clusterrole=cluster-admin --serviceaccount=default:kubeapps-operator
echo "Here is the key :"
echo ""
KEY=$(kubectl get secret $(kubectl get serviceaccount kubeapps-operator -o jsonpath='{range .secrets[*]}{.name}{"\n"}{end}' | grep kubeapps-operator-token) -o jsonpath='{.data.token}' -o go-template='{{.data.token | base64decode}}' && echo)
echo $KEY
echo ""
# Create port forward for testing
echo "[5] Create port forwarding"
kubectl expose service kubeapps --type=NodePort --target-port=8080 --name=kubeapps-internal-dashboard-np -n kubeapps

NODE_PORT=$(kubectl -n kubeapps describe service kubeapps-internal-dashboard-np|grep NodePort:|awk -F '>  ' {'print $2'}|awk -F '/' {'print $1'})

echo "[6] Create PV and PVC for testing"
sleep 2
mkdir /mnt/data
kubectl create -f pv.yml
echo ""
sleep 2
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "YOU CAN KNOW TEST KUBEAPPS WITH THE FOLLOWING URL : $url_first-$NODE_PORT-$url_second !!"
echo "USE FOLLOWING ACCESS KEY : "
echo "$KEY"
