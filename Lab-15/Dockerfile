FROM ubuntu
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get install apache2 sed -y
RUN sed -i 's/80/8087/g' /etc/apache2/ports.conf

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]

