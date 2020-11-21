!#/bin/bash
echo "Copy SSH keys on remote hosts"
sudo ssh-copy-id -i ~/.ssh/id_rsa.pub vagrant@k3s
sudo ssh-copy-id -i ~/.ssh/id_rsa.pub vagrant@gitlab
echo "Test Ansible connection"
ansible -m ping -i ~/ansible/inventory.ini all
