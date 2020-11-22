!#/bin/bash
echo "[1] Git Clone helloworld app from repo"
ssh vagrant@192.168.56.12 'sudo yum install git -y'
ssh vagrant@192.168.56.12 'git-force-clone https://github.com/skynet86/hello-world-k8s.git'
echo "[2] Install app with kubectl command"
ssh vagrant@192.168.56.12 'kubectl create -f /home/vagrant/hello-world-k8s/hello-world.yaml'
echo "[3] Open your browser at the following address :"
echo "http://192.168.56.12:30081"
