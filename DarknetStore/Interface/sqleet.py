#!/usr/bin/env python3
from subprocess import Popen, PIPE
from sqlalchemy import text

class SQLeet():
    def __init__(self, exec_path: str, db_name: str, pw: str):
        """Establish connection to encrypted SQLite3 database

        Args:
            exec_path (str): path to sqleet executable
            db_name (str): filename of db to connect to
            pw (str): password for the database
        """
        self.exec_path: str = exec_path
        self.db_name: str = db_name
        self.proc: Popen = None
        self.pw: str = pw
    
    def __decrypt(self) -> Popen:
        cmd = f"{self.exec_path} {self.db_name} -cmd \"PRAGMA key='{self.pw}';\""
        self.proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    
    def run(self, query: str) -> tuple:
        if not self.proc:
            self.__decrypt()
        
        query = text(query).text.encode()
        ret = self.proc.communicate(query)     
        return (ret, self.proc.returncode)