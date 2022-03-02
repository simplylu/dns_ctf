DarknetStore CTF
===
![Screenshot of the Customer Panel](https://md.js-on.de/uploads/upload_168757b64b049e5209c2c9929208299a.png)
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
docker build . -t dns_ctf
docker run -it dns_ctf /bin/bash

# See hints after startup!
```
![View after startup](https://md.js-on.de/uploads/upload_c092ec3138e25f825d4dc2befd8bb087.png)