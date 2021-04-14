# About
Date : 14th Apr 2021  
Author: Lionel Gurret  
Description : Configure an Ansible Lab with Docker ! (/!\ Don't use it on Production /!\)  
Inspired by : https://github.com/goffinet and https://xavki.blog/ :)  
# Prerequisites
This script is designed for Minikube !  
(https://kubernetes.io/fr/docs/tutorials/hello-minikube/ - Click on Launch Terminal)  
# How to run the lab
`git clone https://github.com/gurretl/labs.git`  
`cd labs/Lab-21`  
`./build-images.sh`
Edit run.sh to specify the number of hosts you need for your Lab (NOF_HOSTS)
`./run.sh`
