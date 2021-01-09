#!/bin/bash
# Lionel Gurret
# 9th Jan 2021

echo "[1] Create a Pod with 2 containers with EmptyDir Volume"
sleep 2
kubectl create -f pod.yml
echo "[2] Install K9S"
(cd && wget https://github.com/derailed/k9s/releases/download/v0.23.10/k9s_Linux_x86_64.tar.gz)
(cd && tar -xzf k9s_Linux_x86_64.tar.gz)
(cd && mv k9s /usr/local/bin/k9s)
sleep 2
while [ "$(kubectl get pod emptydir -o jsonpath='{.items[*].status.containerStatuses[0].ready}')" != "true" ]; do
   sleep 5
   echo "Waiting for Pod to be ready."
done
echo "[3] Copy a dummy file on first container"
echo ""
kubectl cp dummy.txt emptydir:/tmp/container-1-dir -c container-1
sleep 2
echo "[4] Check that the file has been copied"
echo ""
kubectl exec emptydir -c container-1 -- ls /tmp/container-1-dir
sleep 2
echo "[5] Check that the file is available on second container"
echo ""
kubectl exec emptydir -c container-2 -- ls /tmp/container-2-dir
sleep 2
echo "That's it ! You can run k9s command to check what have been done."
