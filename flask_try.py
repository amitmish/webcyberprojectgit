from flask import Flask, redirect, url_for, render_template, request, session
import sys
import pyrebase
import random
import time

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
app = Flask(__name__, template_folder='')
app.secret_key = "any random string"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/static/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        checker = 0
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["email"] = email
            session["password"] = password
            session["logged_in"] = True
            checker = 1
            logged_in = True
        except:
            checker = 0
        if checker == 1:
            session["token"] = user["localId"]
            return redirect("/static/main_info")
        else:
            return render_template("static/login_fail.html")
        #return redirect("/{0}".format(user))
        #return redirect(url_for("user", usr=user))
    else:
        return render_template("static/login.html")

#@app.route("/<usr>")
#def user(usr):
    #return "<h1>{0}</h1>".format(usr)

@app.route("/static/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        checker = 0
        try:
            user = auth.create_user_with_email_and_password(email, password)
            checker = 1
            session["email"] = email
            session["password"] = password
            session["logged_in"] = True
        except:
            checker = 0
        if checker == 1:
            session["token"] = user["localId"]
            return redirect("/static/main_info")
        else:
            return render_template("static/register_fail.html")
    else:
        return render_template("static/register.html")

@app.route("/static/reset_password", methods=["POST", "GET"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        password = ""
        checker = 0
        try:
            user = auth.send_password_reset_email(email)
            checker = 1
            session["email"] = ""
            session["password"] = ""
            session["logged_in"] = False
            session["token"] = ""
        except:
            checker = 0
        if checker == 1:
            return "<h1>HEllo</h1>"
        else:
            return render_template("static/reset_password_fail.html")
    else:
        return render_template("static/reset_password.html")

@app.route("/static/main_info")
def main_info():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        game_room = db.child("users").child(session.get('token')).child("game room").get().val()
        points = db.child("users").child(session.get('token')).child("points").get().val()
        return render_template("static/main_info.html", email = session.get('email').split('@')[0], game_room = game_room, points = points)

if __name__ == "__main__":
    app.run(host='192.168.1.29', port='12345')