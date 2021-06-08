#!/bin/bash
# Lionel Gurret
# 20th Mar 2021

echo "[1] Create an ArgoCD namespace"
sleep 2
kubectl create ns argocd
echo "[2] Install ArgoCD"
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
sleep 10
echo "[3] Configure Network"
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
ARGO_PORT=$(kubectl get -o jsonpath="{.spec.ports[0].nodePort}" services argocd-server -n argocd)
sleep 2
echo "[4] Create our first app (you can do it through the webinterface too !)"
kubectl -n argocd apply -f app.yml
PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo ""
echo "*****************************************************************"
echo "You can now play with ArgoCD on port : $ARGO_PORT !"
echo "Here is your admin password (please change it) : $PASSWORD"
echo "It's possible that the application is not available immediatly"
echo "Please wait or edit a apply a small change :)
echo "*****************************************************************"
