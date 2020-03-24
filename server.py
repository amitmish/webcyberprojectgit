import socket
import sys
import pyrebase
from thread import *
from easygui import *
import random
import time
import tkinter as tk
import thread
import threading
from flask import Flask, redirect, url_for, render_template, request

config = {
    "apiKey": "AIzaSyC3FBTMBznkfl9flr0OGzw4DLpsEMWcbms",
    "authDomain": "cyberproject-5c86e.firebaseapp.com",
    "databaseURL": "https://cyberproject-5c86e.firebaseio.com",
    "projectId": "cyberproject-5c86e",
    "storageBucket": "cyberproject-5c86e.appspot.com",
    "messagingSenderId": "990378544096",
    "appId": "1:990378544096:web:8f088f6dffeb1882fd7985",
    "measurementId": "G-VRMTBMVN04"
};
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
# Get a reference to the auth service
auth = firebase.auth()



HOST = '127.0.0.1'  # Symbolic name meaning all available interfaces
PORT = 10002  # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

# Start listening on socket
s.listen(10)
print 'Socket now listening'


# Function for handling connections. This will be used to create threads
def clientthread(conn):
    # Sending message to connected client
    conn.
    # infinite loop so that function do not terminate and thread do not end.
    while True:
        app = Flask(__name__, template_folder='')

    @app.route("/")
    def home():
        conn.send(render_template("index.html"))

    email = ""
    password = ""

    @app.route("/static/login", methods=["POST", "GET"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            return redirect("/{0}".format(user))
            # return redirect(url_for("user", usr=user))
        else:
            return render_template("static/login.html")

    @app.route("/<usr>")
    def user(usr):
        return "<h1>{0}</h1>".format(usr)

    @app.route("/static/register")
    def register():
        return render_template("static/register.html")

    @app.route("/static/reset_password")
    def reset_password():
        return render_template("static/reset_password.html")
    conn.close()


# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread, (conn,))

s.close()