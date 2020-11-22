!#/bin/bash
servers=`cat servers.lst`
echo "[1] Install Ansible on Controller and sshpass"
sudo apt install ansible sshpass -y
echo "[2] Configure hosts file"
echo "\
192.168.56.10 deploy
192.168.56.12 k3s
" | sudo tee /etc/hosts
echo "[3] Create ansible working dir"
if [ ! -d ~/ansible ]; then
	mkdir ~/ansible
fi
echo "[4] Create and Push SSH Keys to remote nodes"
ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa <<< yes
for server in $servers
do 
    read -p "Vagrant Password for $server ?" password
    sudo sshpass -p"$password" ssh-copy-id -o StrictHostKeyChecking=no\
    -i ~/.ssh/id_rsa vagrant@$server
done
echo "[5] Test ansible connection"
ansible -m ping -i inventory.ini all

