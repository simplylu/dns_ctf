#!/usr/bin/env python3
import base64
import os
import subprocess

from sqleet import SQLeet
from flask import Flask, redirect, render_template, request, session
from typing import Tuple
import sqlite3

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(31)
app.config["DB"] = "/opt/DarknetStore/Interface/customers.db"
app.config["HOST"] = "0.0.0.0"
app.config["PORT"] = 80
app.config["MAIL_DIR"] = "/home/pi/Mails"
app.jinja_env.filters['zip'] = zip

def connect2db() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(app.config["DB"])
    cur = con.cursor()
    return (con, cur)

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

@app.route("/", methods=["GET"])
def index():
    return render_template("portal.html", role=session.get("role", None), userid=session.get("userid", None))

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_authorized():
        return render_template("portal.html", role=session.get("role", None), userid=session.get("userid", None))
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
        except:
            return render_template("login.html", msg="invalid request data"), 401
        if not (username and password):
            return render_template("login.html", msg="invalid request data"), 401
        if username == "Administrator" and password == "hoffnung!":
            session["active"] = True
            session["role"] = "admin"
            session["userid"] = base64.b32encode("Administrator".encode()).decode()
            return render_template("portal.html", role=session.get("role", None), userid=session.get("userid", None))
        elif username == "Armida.Strauss" and password == "THURASOE07":
            session["active"] = True
            session["role"] = "user"
            session["userid"] = base64.b32encode("Armida.Strauss".encode()).decode()
            return render_template("portal.html", role=session.get("role", None), userid=session.get("userid", None))
    else:
        return render_template("login.html", msg="invalid request method"), 401

@app.route("/logout", methods=["GET"])
def logout():
    session["active"] = False
    session["role"] = ""
    session["userid"] = ""
    return render_template("portal.html", role=session.get("role", None), userid=session.get("userid", None))

@app.route("/wp-content", methods=["GET"])
def GET_wp_data():
    return "Don't you dare to go even further!!!", 451

@app.route("/wp-contents", methods=["GET"])
def GET_wp_datas():
    return "Don't you dare to go even further!!!", 451

@app.route("/wp-<string>", methods=["GET"])
def GET_wp_anything(string: str):
    return f"No <b>content</b> here at /wp-{string}"

@app.route("/wp-content/mails", methods=["GET"])
def GET_wp_data_mails():
    emails = os.listdir(app.config["MAIL_DIR"])
    return render_template("emails.html", emails=emails)

@app.route("/wp-content/emails", methods=["GET"])
def GET_wp_data_emails():
    emails = os.listdir(app.config["MAIL_DIR"])
    return render_template("emails.html", emails=emails)

@app.route("/mail/<mail>", methods=["GET"])
def GET_email(mail: str):
    print("MAIL:", mail)
    return open(app.config["MAIL_DIR"] + "/" + mail, 'r').read()

@app.route("/thereIsNoWayThat-You-CanBeThere/")
def GET_tinwtycbts():
    return "Great job, <a href='/wp-content'>this</a> is your reward!"

@app.route("/thereIsNoWayThat-You-CanBeThere")
def GET_tinwtycbt():
    return "Great job, <a href='/wp-content'>this</a> is your reward!"

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if not is_authorized():
        return login()
    if request.method == "POST":
        return settings()
    elif request.method == "GET":
        query_string = request.query_string.decode().split("&")
        for entry in query_string:
            if entry.startswith("user="):
                userid = entry.replace("user=", "")
                try:
                    username = base64.b32decode(userid.encode()).decode()
                except:
                    return "Userid has wrong format", 500
                S = SQLeet(os.path.join(os.environ["SQLEET"], "sqleet"), os.path.join(os.environ["INTERFACE"], "customers.db"), "secret")
                res = S.run(f"""SELECT * FROM customers WHERE username="{username}";""")
                if res[0][0][4:].decode("utf-8") == '':
                    return f"No data available for user '{username}'", 404
                return render_template("settings.html", userid=userid, data=str(res), username=username)
        return "Missing parameter ?user=userid", 500
    else:
        return "Method not allowed", 405

@app.route("/upload_profile", methods=["POST"])
def POST_upload_profile():
    if not is_authorized():
        return login()
    if len(list(request.files.keys())) == 0:
        return redirect(request.referrer), 400
    file = request.files[list(request.files.keys())[0]]
    if file.filename == "":
        return redirect(request.referrer), 400
    if file:
        fname = os.path.join(os.environ["INTERFACE"], "static/img/profile.svg")
        file.save(fname)
        try:
            drawing = svg2rlg(fname)
            renderPM.drawToFile(drawing, os.path.join(os.environ["INTERFACE"], "static/img/profile.png"), fmt="PNG")
            return redirect(request.referrer), 200
        except Exception as e:
            os.remove(fname)
            return redirect(request.referrer), 400

@app.route("/upload_contract", methods=["POST"])
def POST_upload_contract():
    if not is_authorized():
        return login()
    if len(list(request.files.keys())) == 0:
        return redirect(request.referrer), 400
    file = request.files[list(request.files.keys())[0]]
    if file.filename == "":
        return redirect(request.url), 400
    if file:
        fname = os.path.join(os.environ["INTERFACE"], "static/gs/contract.ps")
        file.save(fname)
        try:
            cmdlist = ["gs", "-q", "-dNOPAUSE", "-dSAFER", "-sDEVICE=ppmraw", "-sOutputFile=/dev/null", "-f", fname]
            proc = subprocess.Popen(args=cmdlist, stderr=subprocess.PIPE)
            stderr = proc.stderr.read()
            if stderr == b'':
                return "Хорошо!", 200
            else:
                return stderr.decode()
        except:
            return "Что-то пошло не так, пожалуйста, попробуйте еще раз!", 400
    return "Еще не реализовано.", 500


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"])