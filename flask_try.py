from flask import Flask, redirect, url_for, render_template, request, session
import sys
import pyrebase
import random
import time
from server_functions import *
import thread
import threading

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
            data = {"email": email, "game room": "none", "points": 0}
            db.child("users").child(session.get("token")).set(data)
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

@app.route("/static/main_join", methods=["POST", "GET"])
def main_join():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            return render_template("static/main_join.html", email = session.get('email').split('@')[0], error = "")
        else:
            token = session.get("token")
            email = session.get("email")
            game_room = request.form["game_room"]
            session["game_room"] = game_room
            subject = db.child("rooms").child(game_room).child("subject").get().val()
            session["subject"] = subject
            if db.child("rooms").child(game_room).child("started").get().val() == 0:
                data = {"email": email, "game room": game_room,
                        "points": db.child("users").child(token).child("points").get().val()}
                db.child("users").child(token).set(data)
                session["q1_num"] = db.child("rooms").child(game_room).child("q1").get().val()
                session["q2_num"] = db.child("rooms").child(game_room).child("q2").get().val()
                session["q3_num"] = db.child("rooms").child(game_room).child("q3").get().val()
                db.child("rooms").child(game_room).child("users_in").update({token: email.split('@')[0]})
                session["room_admin"] = False
                return redirect("/static/before_game")
            else:
                return render_template("static/main_join.html", email = session.get('email').split('@')[0], error = "Wrong Game Room")

@app.route("/static/main_create", methods=["POST", "GET"])
def main_create():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            return render_template("static/main_create.html", email = session.get('email').split('@')[0], error = "")
        else:
            session["subject"] = request.form["subject"]
            subject = session.get("subject")
            token = session.get("token")
            email = session.get("email")
            game_room = random.randint(1, 10000)
            found_code = False
            while found_code == False:
                if db.child("rooms").child(game_room).child("started").get().val() == 1:
                    game_room = random.randint(1, 10000)
                else:
                    found_code = True
            data = {"email": email, "game room": game_room,
                    "points": db.child("users").child(token).child("points").get().val()}
            db.child("users").child(token).set(data)

            questions = {"subject": subject, "admin": token, "started": 0, "finished": 0, "q1": get_random_int(subject), "q2": get_random_int(subject), "q3": get_random_int(subject), "best score": 1000, "best player": "none"}
            db.child("rooms").child(game_room).set(questions)

            db.child("rooms").child(game_room).child("users_in").update({token: email.split('@')[0]})

            session["game_room"] = game_room
            session["room_admin"] = True
            session["q1_num"] = db.child("rooms").child(game_room).child("q1").get().val()
            session["q2_num"] = db.child("rooms").child(game_room).child("q2").get().val()
            session["q3_num"] = db.child("rooms").child(game_room).child("q3").get().val()
            return redirect("/static/before_game")


@app.route("/static/add_question", methods=["POST", "GET"])
def add_question():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            return render_template("static/add_question.html", email=session.get('email').split('@')[0], error = "")
        else:
            subject = request.form["subject"]
            answer = request.form["answer"]
            question = request.form["question"]
            if subject == "select" or answer == "" or question == "":
                return render_template("static/add_question.html", email=session.get('email').split('@')[0], error = "Check Inputs")
            else:
                add_question_to_db(question, answer, subject)
                return redirect("/static/main_info")

@app.route("/static/before_game", methods=["POST", "GET"])
def before_game():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            if session.get("room_admin") == True:
                return render_template("static/before_game_admin.html", email=session.get('email').split('@')[0], game_room=session.get("game_room"), token=session.get("token"))
            else:
                return render_template("static/before_game_not_admin.html", email=session.get('email').split('@')[0], game_room=session.get("game_room"), token=session.get("token"))
        else:
            return redirect("/static/game")


@app.route("/static/game", methods=["POST", "GET"])
def game():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        session["start_time"] = time.time()
        subject = session.get("subject")
        game_room = session.get("game_room")
        if request.method == "GET":
            if session.get("room_admin") == True:
                t = threading.Thread(target=open_room, args=(session.get("game_room"),))
                t.start()
                db.child("rooms").child(session.get("game_room")).update({"started":1})
            q1_num = session.get("q1_num")
            q2_num = session.get("q2_num")
            q3_num = session.get("q3_num")
            q1 = db.child("questions").child(subject).child("q" + str(q1_num)).child("question").get().val()
            q2 = db.child("questions").child(subject).child("q" + str(q2_num)).child("question").get().val()
            q3 = db.child("questions").child(subject).child("q" + str(q3_num)).child("question").get().val()
            return render_template("static/game.html", email = session.get('email').split('@')[0], q1 = q1, q2 = q2, q3 = q3, game_room = session.get("game_room"))
        else:
            q1_ans = request.form["q1_ans"]
            q2_ans = request.form["q2_ans"]
            q3_ans = request.form["q3_ans"]
            session["q1_ans"] = q1_ans
            session["q2_ans"] = q2_ans
            session["q3_ans"] = q3_ans
            return redirect("/static/finished")

@app.route("/static/finished")
def finished():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        subject = session.get("subject")
        game_room = session.get("game_room")
        email = session.get("email")
        token = session.get("token")
        end = time.time()
        countTrue = 0
        wrongAnswerTime = 0
        number_of_question_1 = db.child("rooms").child(game_room).child("q1").get().val()
        number_of_question_2 = db.child("rooms").child(game_room).child("q2").get().val()
        number_of_question_3 = db.child("rooms").child(game_room).child("q3").get().val()
        q1_ans = session.get("q1_ans")
        q2_ans = session.get("q2_ans")
        q3_ans = session.get("q3_ans")
        if q1_ans == "":
            q1_ans = -1
        if q2_ans == "":
            q2_ans = -1
        if q3_ans == "":
            q3_ans = -1
        if int(db.child("questions").child(subject).child("q" + str(number_of_question_1)).child("answer").get().val()) == int(
                q1_ans):
            countTrue += 1
        else:
            wrongAnswerTime += 7
        if int(db.child("questions").child(subject).child("q" + str(number_of_question_2)).child("answer").get().val()) == int(
                q2_ans):
            countTrue += 1
        else:
            wrongAnswerTime += 7
        if int(db.child("questions").child(subject).child("q" + str(number_of_question_3)).child("answer").get().val()) == int(
                q3_ans):
            countTrue += 1
        else:
            wrongAnswerTime += 7
        score = int(end - session.get("start_time") + wrongAnswerTime) - int(countTrue)
        if score < db.child("rooms").child(game_room).child("best score").get().val():
            db.child("rooms").child(game_room).child("best score").set(score)
            db.child("rooms").child(game_room).child("best player").set(token)
        return render_template("static/finished.html", email=session.get('email').split('@')[0], game_room=session.get("game_room"))


@app.route("/static/result", methods=["POST", "GET"])
def result():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            game_room = session.get("game_room")
            token = session.get("token")
            winnerToken = db.child("rooms").child(game_room).child("best player").get().val()
            winnerName = db.child("rooms").child(game_room).child("users_in").child(winnerToken).get().val()
            winnerPoints = db.child("users").child(winnerToken).child("points").get().val()
            if winnerPoints == None:
                winnerPoints = 0
            db.child("users").child(winnerToken).update({"points": winnerPoints + 1})
            if winnerToken != token:
                userPoints = db.child("users").child(token).child("points").get().val()
                db.child("users").child(token).update({"points": userPoints - 1})
            return render_template("static/result.html", email=session.get('email').split('@')[0], game_room = game_room, winner = winnerName)
        else:
            return redirect("/static/main_info")
if __name__ == "__main__":
    app.run(host='192.168.1.29', port='12345')