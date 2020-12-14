# About
Date : 22 Nov 2020  
Author: Lionel Gurret  
Description : Install K3S env from Ansible Controller on a VM !
# LinkedIn article related
# Prerequisites
2 Virtual machines (Check Lab-1 for Vagrant Files examples):  
* First VM :  
    * hostname: deploy
    * IP : 192.168.56.10
    * vCPU : 2
    * RAM : 2GB
    * OS : Ubuntu (GUI)
* Second VM : K3S 2vCPUs and 2GB RAM  
    * hostname: k3s
    * IP : 192.168.56.12
    * vCPU : 2
    * RAM : 2GB
    * OS : Centos7
# How to launch the Lab
From Deploy VM, run the following commands :  
`git clone https://github.com/gurretl/labs`  
`cd labs`  
`./1-controller-config.sh`  
`./2-run-playbook.sh`  
`-/3-install-helloworld-app.sh`  
