!#/bin/bash
echo "[1] Create role(s) directory"
if [ ! -d ~/.ansible/roles ]; then
	mkdir ~/.ansible/roles
fi
echo "[2] Install role(s)"
ansible-galaxy install -r requirements.yml -p ~/.ansible/roles
echo "[3] Run Playbook to install K3S"
ansible-playbook -i inventory.ini playbook.yml -vv
