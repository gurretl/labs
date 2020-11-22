!#/bin/bash
echo "[1] Create role directory"
if [ ! -d ~/.ansible/roles ]; then
	mkdir ~/.ansible/roles
fi
echo "[2] Install roles"
ansible-galaxy install -r requirements.yml -p ~/.ansible/roles
echo "[3] Run Playbook to install GitLab and K3S"
ansible-playbook -i inventory.ini playbook.yml -vv
