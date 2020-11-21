#!/bin/bash

echo "[1] : change keyboard layout to Swiss"
sudo sed -i 's/XKBLAYOUT=\"\w*"/XKBLAYOUT=\"ch\"/g' /etc/default/keyboard

echo "[2]: Install docker if not exist"
if [ ! -f "/usr/bin/docker" ];then
curl -s -fsSL https://get.docker.com | sh; 
fi

echo "[3]: Install GUI"
pkg="ubuntu-desktop"
if dpkg -s $pkg
then
    echo "$pkg installed"
else
    echo "$pkg not installed"
    sudo apt-get update -y && sudo apt-get upgrade -y
	sudo apt-get install ubuntu-desktop -y
	sudo reboot
fi

echo "[4]: Install packages"
sudo apt-get install mc net-tools git ansible -y
