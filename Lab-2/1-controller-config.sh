!#/bin/bash
sudo apt install ansible -y
echo "\
192.168.56.10 deploy
192.168.56.11 gitlab
192.168.56.12 k3s
" | sudo tee /etc/hosts
ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa <<< yes
if [ ! -d ~/ansible ]; then
	mkdir ~/ansible
fi
touch /home/vagrant/ansible/inventory.ini
echo "\
ks3 ansible_ssh_user=vagrant ansible_ssh_private_key_file=~/.ssh/id_rsa
gitlab ansible_ssh_user=vagrant ansible_ssh_private_key_file=~/.ssh/id_rsa" > /home/vagrant/ansible/inventory.ini

