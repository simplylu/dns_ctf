#!/usr/bin/env python3
import base64
from subprocess import Popen, PIPE
from getpass import getpass
from os import getuid
import os
import sys
from sqlalchemy import text

class SQLeet():
    def __init__(self, exec_path: str, db_name: str, pw: str):
        self.exec_path: str = exec_path
        self.db_name: str = db_name
        self.proc: Popen = None
        self.pw: str = pw

    def __decrypt(self) -> Popen:
        cmdlist = [self.exec_path, self.db_name, "-cmd", f""""PRAGMA key='{self.pw}';" """]
        self.proc = Popen(' '.join(cmdlist), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def run(self, query: str) -> tuple:
        if not self.proc:
            self.__decrypt()
        
        query = text(query).text
        ret = self.proc.communicate(query.encode())  
        return (ret, self.proc.returncode)


def help():
    print("Usage: ./keyring [get|set|del] SERVICE USERNAME\n")
    print("Options:")
    print("  -h, --help            show this help message and exit")
    print("  -p KEYRING_PATH, --keyring-path=KEYRING_PATH")
    print("                        Path to the keyring backend")
    print("  -b KEYRING_BACKEND, --keyring-backend=KEYRING_BACKEND")
    print("                        Name of the keyring backend")
    print("  --list-backends       List keyring backends and exit")
    print("  --disable             Disable keyring and exit")
    sys.exit(0)


def connect_to_keyring() -> SQLeet:
    return SQLeet(os.path.join(os.environ["SQLEET"], "sqleet"), os.path.join(os.environ["KEYRING"], "keyring.db"), "~^.m)wuit8I3oA)Z<cOS/m0U[;N7HRwbAs.UNW7/")


def check_root():
    if getuid() != 0:
        print("Be root to be able to use all functions!")
        sys.exit(0)


def set_pw(key: str, name: str, pw: str = None):
    S = connect_to_keyring()
    key = f"{key}.{name}"
    if not pw:
        pw = getpass(f"Password for '{name}' in '{key}': ")
    pw = base64.encodebytes(pw.encode()).decode("utf-8")
    ret, code = S.run(f"""INSERT INTO keys(key, pw) VALUES('{key}', '{pw}');""")
    if code == 0:
        print(ret[0].decode())
    else:
        del S
        S = connect_to_keyring()
        ret, code = S.run(f"""UPDATE keys SET pw='{pw}' WHERE key='{key}';""")
        if code == 0:
            print(f"Updated password for '{name}' in '{key}'")
        else:
            print(ret, code)
    sys.exit(0)


def get_pw(key: str, name: str):
    check_root()
    S = connect_to_keyring()
    key = f"{key}.{name}"
    ret, _ = S.run(f"""SELECT pw FROM keys WHERE key="{key}";""")
    if ret[0] == b'ok\n':
        sys.exit(0)
    else:
        pw = base64.decodebytes(ret[0][3:-1]).decode("utf-8")
        print(f"Password: {pw}")
    sys.exit(0)


def del_pw(key: str, name: str):
    check_root()
    S = connect_to_keyring()
    key = f"{key}.{name}"
    ret, code = S.run(f"""DELETE FROM keys WHERE key='{key}'';""")
    if code == 0:
        print(f"Successfully deleted password for '{name}' in '{key}'")
    sys.exit(0)

# a';"; cat /etc/passwd; echo "'

try:
    if sys.argv[1] == "set":
        key = sys.argv[2]
        name = sys.argv[3]
        try:
            pw = sys.argv[4]
        except:
            pw = None
        set_pw(key, name, pw)
    elif sys.argv[1] == "get":
        key = sys.argv[2]
        name = sys.argv[3]
        get_pw(key, name)
    elif sys.argv[1] == "del":
        key = sys.argv[2]
        name = sys.argv[3]
        del_pw(key, name)
    elif sys.argv[1] == "--list-backends":
        print("[i] Not yet implemented!")
    elif sys.argv[1] == "--disable":
        print("[i] Not yet implemented!")
    elif sys.argv[1] in ["--help", "-h"]:
        help()
    else:
        help()
except Exception as e:
    help()
