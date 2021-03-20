#!/bin/bash
# Lionel Gurret
# 20th Mar 2021

echo "[1] Create an ArgoCD namespace"
sleep 2
kubectl create ns argocd
echo "[2] Install ArgoCD"
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
sleep 2
while [ "$(kubectl get pods -n argocd -o jsonpath='{.status.phase}')" != "Running" ]; do
   sleep 5
   echo "Waiting for Pods to be ready."
done
echo "[3] Configure Network"
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
ARGO_PORT=$(kubectl get -o jsonpath="{.spec.ports[0].nodePort}" services argocd-server -n argocd)
sleep 2
echo "[4] Check that the file has been copied"
sleep 2
echo ""
echo "******************************************************"
echo "You can now play with ArgoCD on port : $ARGO_PORT !"
echo "******************************************************"

