FROM ubuntu:latest

# Install dependencies
RUN apt update -y
RUN apt install gcc zlib1g zlib1g-dev make wget unzip libdata-compare-perl -y

# Install OpenSSL (see INSTALL for more information)
RUN wget -c "https://www.openssl.org/source/old/1.0.2/openssl-1.0.2u.tar.gz"
RUN gunzip openssl-1.0.2u.tar.gz
RUN tar -xvf openssl-1.0.2u.tar
WORKDIR /openssl-1.0.2u/
RUN ./config
RUN make
RUN make test
RUN make install

RUN rm -rf /usr/bin/openssl
RUN ln -s /usr/local/ssl/bin/openssl /usr/bin/openssl
# openssl version should output: OpenSSL 1.0.2u  20 Dec 2019

# Install OpenSSH (see INSTALL for more information)
WORKDIR /
RUN wget -c "http://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-7.6p1.tar.gz"
RUN gunzip openssh-7.6p1.tar.gz
RUN tar -xvf openssh-7.6p1.tar
WORKDIR /openssh-7.6p1/
RUN ./configure
RUN make
RUN make install
# ssh -V should output: OpenSSH_7.6p1, OpenSSL 1.0.2u 20 Dec 2019

# Reconfigure and start SSH Server
RUN adduser sshd
RUN sed -i 's/#Port 22/Port 443/g' /usr/local/etc/sshd_config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/g' /usr/local/etc/sshd_config
RUN echo "\nAllowUsers pi" >> /usr/local/etc/sshd_config

# Install GhostScript
# RUN apt install freetype lcms2 jpeg libpng zlib build-base
WORKDIR /
RUN wget -c "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs921/ghostscript-9.21.tar.gz"
RUN tar xzvf ghostscript-9.21.tar.gz
WORKDIR /ghostscript-9.21/
RUN ./configure --prefix=/usr --disable-compile-inits --enable-dynamic --with-system-libtiff
RUN make
RUN make install

RUN apt install netcat -y
EXPOSE 443

# Set wrong access rights for /etc/shadow
RUN apt install acl -y
RUN useradd flask
RUN usermod --password '$1$I.7Fkpnq$PZ/PBhiIiK0.RuFmGfLY01' flask

# Add default user pi with password "raspberry" and add home dir
RUN useradd pi
RUN usermod --password '$1$AuhU9AU4$UUpE02B2t5BOU7cL2fUI/.' pi
RUN mkhomedir_helper pi

# Add flag user to appear in /etc/shadow
RUN useradd its_1m_b3h1nd_y0u_

# Install requirements for the DarknetStore
RUN apt install python3 python3-pip git authbind -y

# Env vars and directory creation
ENV FLASK=/opt/DarknetStore
ENV ADMIN=/opt/DarknetStore/Admin
ENV INTERFACE=/opt/DarknetStore/Interface
ENV SQLEET=/opt/sqleet
ENV KEYRING=/opt/Keyring
WORKDIR /opt
RUN mkdir ${FLASK}
RUN mkdir ${ADMIN}
RUN mkdir ${INTERFACE}
RUN mkdir ${SQLEET}
RUN mkdir ${KEYRING}

# Install sqleet from Git
# Install sqleet dependencies
RUN apt install glibc-source -y
WORKDIR /opt
RUN git clone https://github.com/resilar/sqleet.git
WORKDIR /opt/sqleet
RUN gcc sqleet.c shell.c -o sqleet -lpthread -ldl

# Clone custom data from GIT
WORKDIR /
RUN mkdir /dns_ctf
COPY requirements.txt /dns_ctf/
RUN pip3 install -r /dns_ctf/requirements.txt
COPY Mails /home/pi/Mails
COPY DarknetStore/README.md ${FLASK}/README.md
COPY DarknetStore/Admin ${ADMIN}
COPY DarknetStore/Admin/templates/nimda.html ${ADMIN}/templates/nimda.html
COPY DarknetStore/Interface ${INTERFACE}
COPY Keyring/ ${KEYRING}

# RUN git clone https://github.com/js-on/dns_ctf.git
# Install python3 modules via pip
# !TODO: Fix for prod
# WORKDIR /dns_ctf/
# RUN cp -r /dns_ctf/DarknetStore/Admin/* ${ADMIN}
# RUN cp -r DarknetStore/Interface/* ${INTERFACE}
# RUN cp -r Keyring/* ${KEYRING}
# RUN mkdir /home/pi/Mails
# RUN cp -r Mails/* /home/pi/Mails/.
RUN chown -R pi:pi /home/pi/Mails/

# Install customer server
RUN touch /etc/authbind/byport/80
RUN chmod 777 /etc/authbind/byport/80
RUN chown -R flask:flask /opt/*

# Set root password
RUN usermod --password '$1$/6/Ngicd$mvvyG72QCfvFWC4vIwU5Z1' root

# Uninstall requirements
WORKDIR /
RUN apt purge gcc make python3-pip git -y
RUN apt autoremove -y
RUN rm -rf /open*
RUN rm -rf /dns_ctf
RUN rm -rf /ghostscript-9.21.tar.gz
RUN apt-get clean -y

RUN echo -n "ITS{c4m3_1n_th3_g4m3_w1th_4_k3y}" > /root/flag.txt
RUN mkdir -p /opt/DarknetStore/.git
COPY .git /opt/DarknetStore/.git/
# Post installation commands
# Set ACL
# Start SSHD
# Do some other neccessary stuff
# Run Flask environment
COPY ./post_installation.sh /tmp/post_installation.sh
WORKDIR /tmp
RUN chmod +x post_installation.sh
ENTRYPOINT [ "./post_installation.sh" ]