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
PASSWORD=$(kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-server -o name | cut -d'/' -f 2)
sleep 5
VOTE_PORT=$(kubectl get -o jsonpath="{.spec.ports[0].nodePort}" services voting-service -n votingapp)
RESULT_PORT=$(kubectl get -o jsonpath="{.spec.ports[0].nodePort}" services result-service -n votingapp)
echo ""
echo "*****************************************************************"
echo "You can now play with ArgoCD on port : $ARGO_PORT !"
echo "Here is your admin password (please change it) : $PASSWORD"
echo "*****************************************************************"
echo "Voting App ports : $VOTE_PORT and $RESULT_PORT"
echo "*****************************************************************"
