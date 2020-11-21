#!/bin/bash

echo "[1]: Install packages"
sudo yum update -y && yum install mc net-tools -y

echo "[2]: Change keyboard to Swiss"
sudo yum install kbd -y
sudo localectl set-keymap ch

echo "[3] : All SSH with Password"
sudo sed -i 's/PasswordAuthentication no\"\w*"/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sudo service sshd restart
