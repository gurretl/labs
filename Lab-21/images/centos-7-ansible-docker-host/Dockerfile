FROM centos/python-35-centos7:latest
USER root
RUN yum install -y openssh-server
RUN mkdir ~/.ssh && ssh-keygen -N "" -t rsa -f ~/.ssh/id_rsa && yum install -y initscripts

COPY common/id_rsa.pub /root/.ssh/authorized_keys
COPY common/start.sh /start.sh

WORKDIR /root

ENV ALLOW_EXIT true

CMD /start.sh