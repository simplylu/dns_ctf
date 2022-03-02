DarknetStore (DNS)
===
Welcome to the DarknetStore.
Installation is easy, as we're working together with Docker for some years now to serve you the best possible darknet offers.

We're cooperating with popular groups and we've granted a price for the best user experience in a DaRkNeT sHoP.

We take personal information very serious!¡! Therefore our customer database is зашифрованный with very strong algorithms and may take a little longer to respond to your requests.

Unfortunately, we discovered together with the the DDOS Team (Dangerous Docker Original Security) a security hole in our SQL Crypto Wrapper. You can find the related files at /opt/.

One of our former students has **not** parsed the output from the Keyring into the SQL Crypto Wrapper correctly. Thus, it was possible to change the password in the keyring to a specific payload. If done right, the payload was executed with superuser permissions.

The customer portal is not affected by this, as we've externalised our API requests. We're currently working on the admin panel, to not use this library anymore. Changes are ongoing, but please secure your keyring as we cannot guarantee, that the Admin panel is safe for Injections via the Keyring.

To give you a better understanding of the security risk, we've provided the affected code for you:
```py
def __decrypt(self) -> Popen:
    """Decrypt database and return process

    Returns:
        Popen: Process with DB connection
    """
    cmd = f"{self.exec_path} {self.db_name} -cmd \"PRAGMA key='{self.pw}';\""
    self.proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

# self.exec_path is the path to the wrapped executable
# self.db_name is the name of the encrypted database
# self.pw is the passwort taken from the keyring
```

Please don't mess with any files in the Keyring directory, otherwise you have to restart the Container (using restart in the dns_ctf shell) and may loose changes!