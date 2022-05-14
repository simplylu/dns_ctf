DarknetStore CTF
===
![Screenshot of the Customer Panel](store.png)
### DNS CTF
DNS is our DarknetShop. It consists of two parts. The customer portal and the admin panel. Your goal is to hack the container and find all the flags using only the knowledge of the IP address and the methods you've learned during your studies. In some cases, there are several ways to get to the flag, so a flag can have two different levels of difficulty, depending on the way chosen. With the exception of URL fuzzing and some password cracking, no bruteforce needs to be applied.

### Rules
- Don't look into the code of this GitHub Repo. It is cheating!
- Don't look into the code of the Dockerfile. It is cheating!
- Don't look into the code of post_installation.sh. It is, again, cheating!

### Installation
```sh
git clone https://github.com/js-on/dns_ctf.git
cd dns_ctf
# Build container and give it the name "dns_ctf"
docker build . -t dns_ctf
# docker image ls should output
# REPOSITORY        TAG           IMAGE ID       CREATED              SIZE
# dns_ctf           latest        a665a8ce39b4   About a minute ago   1.12GB
# Run container in interactive mode (to enable dns_ctf shell)
docker run -it dns_ctf /bin/bash

# See hints after startup!
```
![View after startup](start.png)

### Troubleshooting
#### Too many authentication failures
This is a common issue when using SSH. Add `-o PreferredAuthentications=password` behind your SSH command and it should work.
#### Failed to export image
If you get the following error, don't worry, just rerun the build command and it should restart the build where it has stopped.
`failed to export image: failed to create image: failed to get layer sha256:[0-9a-f]{64}: layer does not exist`
