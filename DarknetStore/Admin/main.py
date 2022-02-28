#!/usr/bin/env python3
import base64
import os
import subprocess

import json
from urllib.parse import unquote_plus

from hashlib import sha1
from sqleet import SQLeet
from flask import Flask, render_template, request, session
from werkzeug.exceptions import Unauthorized
from typing import Tuple
import sqlite3
import requests
from sqlalchemy import text

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(31)
app.config["DB"] = "customers.db"
app.config["HOST"] = "0.0.0.0"
app.config["PORT"] = 81
app.jinja_env.filters['zip'] = zip

def connect2db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(app.config["DB"])
    cur = con.cursor()
    return (con, cur)

def __fetch_pw_from_keyring() -> str:
    pw = subprocess.check_output(["python3", os.path.join(os.environ["SQLEET"], "keyring.py"), "get", "system", "customer_db"])
    if b"Password" in pw:
        pw = pw[10:-1].decode()
        return pw
    else:
        print("Password could not be fetched from keyring.")
        print("Make sure, a key for 'customer_db' exists in 'system'.")
        return ""

def is_authorized():
    try:
        return session["active"]
    except:
        return False

def is_admin():
    try:
        return session["active"] and session["role"] == "admin"
    except:
        return False

ALLOWED_QUERIES = ["logic", "firstname", "surname", "username", "email", "city", "district", "postcode", "street", "housenumber", "iban", "bic", "shoppingcart"]

@app.route("/nimda", methods=["GET"])
def nimda(data: list = [], msg: str = "", dberror: dict = None):
    if is_admin():
        return render_template("nimda.html", role=session["role"], data=data, faces=requests.get(f"https://faceapi.herokuapp.com/faces?n={len(data)}").json(), msg=msg, dberror=dberror)
    else:
        return login(), 401

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_authorized():
        return nimda()
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
        except:
            return render_template("login.html", msg="invalid request data"), 401
        if not (username and password):
            return render_template("login.html", msg="invalid request data"), 401
        if username == "Administrator":
            if password == "hoffnung!":
                session["active"] = True
                session["role"] = "admin"
                session["userid"] = base64.b32encode("Administrator".encode()).decode()
                return nimda()
            else:
                return render_template("login.html", msg="invalid user or password"), 401
        try:
            S = SQLeet(os.path.join(os.environ["SQLEET"], "sqleet"), "customers.db", __fetch_pw_from_keyring())
            res = S.run(f"""SELECT password,role FROM customers WHERE username="{username}";""")
            data = res[0][0]
            if data.decode("utf-8")[4:] == '':
                return render_template("login.html"), 401
            pwhash, role = res[0][0][3:-1].decode().split("|")
            if sha1(password.encode()).hexdigest() == pwhash:
                session["active"] = True
                session["role"] = role
                session["userid"] = base64.b32encode(username.encode()).decode()
                return nimda()
            else:
                return render_template("login.html", msg="invalid user or password"), 401
        except Exception as e:
            return render_template("login.html", msg="something went wrong"), 401
    else:
        return render_template("login.html", msg="invalid request method"), 401

@app.route("/logout", methods=["GET"])
def logout():
    session["active"] = False
    session["role"] = ""
    session["userid"] = ""
    return login()

@app.route("/search", methods=["GET"])
def search():
    if not is_admin():
        raise Unauthorized
    try:
        query_string = request.query_string.decode().split("&")
    except:
        return nimda(msg="Something went wrong")
    
    sql_parts = []
    logic = ""
    for field in query_string:
        key, val = field.split("=")
        key = unquote_plus(key)
        val = unquote_plus(val)
        if key not in ALLOWED_QUERIES:
            return nimda(msg="Don't try to SQLi or **** me!")
        if key == "logic":
            logic = val
            continue
        if not val:
            continue
        if key == "shoppingcart":
            val = "%" + val + "%"
        if "*" in val:
            val = val.replace("*", "%")
        if "%" in val:
            sql_parts.append(f'{key} LIKE "{val}"')
        else:
            sql_parts.append(f'{key}="{val}"')
    
    if not sql_parts:
        return nimda(msg="At least one query parameter needed")
    parts = text(f" {logic.upper()} ".join(sql_parts)).text
    sql = f"SELECT * FROM customers WHERE {parts};"
    S = SQLeet(os.path.join(os.environ["SQLEET"], "sqleet"), "customers.db", __fetch_pw_from_keyring())
    res, ret = S.run(sql)
    if ret == 0:
        stdout = res[0].decode("utf-8")
        stderr = res[1].decode("utf-8")
        if stderr != '':
            return nimda(msg="Error, will be fixed soon", dberror={"stdout": res[0], "stderr": res[1]})
        else:
            data = []
            stdout = stdout[4:].split("\n")
            for line in stdout:
                line = line.split("|")
                if len(line) == 1:
                    continue
                data.append({
                    "firstname": line[1],
                    "surname": line[2],
                    "username": line[3],
                    "email": line[4],
                    "phone": line[5],
                    "city": line[6],
                    "district": line[7],
                    "zip": line[8],
                    "street": line[9],
                    "housenumber": line[10],
                    "iban": line[12],
                    "bic": line[13],
                    "shoppingcart": json.loads(line[15])
                })
            return nimda(data=data)
    else:
        return nimda(msg="Error, will be fixed soon", dberror={"stdout": res[0], "stderr": res[1]})

if __name__ == "__main__":
    # TODO: While loop here or in bash starter?
    app.run(host=app.config["HOST"], port=app.config["PORT"])