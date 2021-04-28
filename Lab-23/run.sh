#!/bin/bash

# Lionel Gurret
# 28th Apr 2021

# Ask for Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)
#echo "Please provie Minikube public URL (ex: https://2886795331-cykoria04.environments.katacoda.com/)"
#read -p "You can get it by clicking on + / Select port to view on Host 1: " answer
#echo "Answer : $answer"

# Split URL to get 2 parts
#url_first=$(echo $answer|awk -F '-' {'print $1'})
#url_second=$(echo $answer|awk -F '-' {'print $2'})

## Install Helm 3.4.1
#(cd && wget https://get.helm.sh/helm-v3.4.1-linux-amd64.tar.gz)
#(cd && tar -zxvf helm-v3.4.1-linux-amd64.tar.gz)
#(cd && mv linux-amd64/helm /usr/local/bin/helm)
## Install k9s
#(cd && wget https://github.com/derailed/k9s/releases/download/v0.23.10/k9s_Linux_x86_64.tar.gz)
#(cd && tar -xzf k9s_Linux_x86_64.tar.gz)
#(cd && mv k9s /usr/local/bin/k9s)

# Install TKN
(cd && curl -LO https://github.com/tektoncd/cli/releases/download/v0.18.0/tkn_0.18.0_Linux_x86_64.tar.gz)
(cd && sudo tar xvzf tkn_0.18.0_Linux_x86_64.tar.gz -C /usr/local/bin/ tkn)

# Install Tekton
(cd && kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml)

# Install first Tekton Task (simple hello world task)
(cd && kubectl apply -f demo/01-hello.yaml)

# Install Second Tekton Task with parameters (task with parameter)
(cd && kubectl apply -f demo/02-param.yaml)

# Install Tekton tasks
(cd && kubrect apply -f demo/03-tasks.yaml)

# Install Tekton Pipeline 
(cd && kubrect apply -f demo/04-pipeline.yaml)

# Display all information
echo "*************************************************************************************************************"
echo "********************************** ENVIRONMENT CONFIGURED YOU CAN PLAY NOW **********************************"
echo "*************************************************************************************************************"
echo "List all tasks : tkn task list"
echo "\n"
echo "Run task : tkn start --showlog <task_name>"
echo "\n"
echo "List Pipelines : tkn pipeline list"
echo "\n"
echo "Run Pipeline: tkn pipeline start <pipeline_name> --showlog"
