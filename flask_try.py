from flask import Flask, redirect, url_for, render_template, request, session
import sys
import pyrebase
import random
import time
from server_functions import *
import thread
import threading
import ssl

#for platform identify
from flask import request

HOST = "192.168.1.29"
PORT = "12345"

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
    return "hello"

@app.route("/static/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session["email"] = ""
        session["password"] = ""
        session["logged_in"] = False
        session["token"] = ""
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
        #platform(android/windows = request.user_agent.platform
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
            data = {"email": email, "game room": "none", "points": 0, "quizzes": 0}
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
        quizzes = db.child("users").child(session.get('token')).child("quizzes").get().val()
        return render_template("static/main_info.html", email = session.get('email').split('@')[0], game_room = game_room, points = points, quizzes=quizzes)

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
                data = {"email": email, "game room": game_room, "points": db.child("users").child(token).child("points").get().val(), "quizzes": db.child("users").child(token).child("quizzes").get().val()}
                db.child("users").child(token).set(data)
                db.child("rooms").child(game_room).child("users_in").update({token: email.split('@')[0]})
                session["room_admin"] = False
                return redirect("/static/before_game")
            else:
                return render_template("static/main_join.html", email = session.get('email').split('@')[0], error = "Wrong Game Room")

@app.route("/static/main_create/")
def redirect_main_create():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    return redirect("/static/main_create/none")


@app.route("/static/main_create/<quiz_name>", methods=["POST", "GET"])
def main_create(quiz_name):
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            if quiz_name != "none":
                token = session.get("token")
                email = session.get("email")
                game_room = random.randint(1, 10000)
                found_code = False
                while found_code == False:
                    if db.child("rooms").child(game_room).child("started").get().val() == 1:
                        game_room = random.randint(1, 10000)
                    else:
                        found_code = True

                session["subject"] = session.get("token")
                subject = session.get("subject")
                q1_num = "q1"
                q2_num = "q2"
                q3_num = "q3"
                q4_num = "q4"
                q5_num = "q5"
                question1 = db.child("questions").child(subject).child(quiz_name).child(q1_num).child(
                    "question").get().val()
                question2 = db.child("questions").child(subject).child(quiz_name).child(q2_num).child(
                    "question").get().val()
                question3 = db.child("questions").child(subject).child(quiz_name).child(q3_num).child(
                    "question").get().val()
                question4 = db.child("questions").child(subject).child(quiz_name).child(q4_num).child(
                    "question").get().val()
                question5 = db.child("questions").child(subject).child(quiz_name).child(q5_num).child(
                    "question").get().val()
                answer1 = db.child("questions").child(subject).child(quiz_name).child(q1_num).child(
                    "answer").get().val()
                answer2 = db.child("questions").child(subject).child(quiz_name).child(q2_num).child(
                    "answer").get().val()
                answer3 = db.child("questions").child(subject).child(quiz_name).child(q3_num).child(
                    "answer").get().val()
                answer4 = db.child("questions").child(subject).child(quiz_name).child(q4_num).child(
                    "answer").get().val()
                answer5 = db.child("questions").child(subject).child(quiz_name).child(q5_num).child(
                    "answer").get().val()

                questions = {"subject": subject, "admin": token, "started": 0, "finished": 0, "question1": question1,
                             "answer1": answer1, "question2": question2, "answer2": answer2, "question3": question3,
                             "answer3": answer3, "question4": question4, "answer4": answer4, "question5": question5, "answer5": answer5, "best score": 1000, "best player": "none"}
                db.child("rooms").child(game_room).set(questions)

                data = {"email": email, "game room": game_room,
                        "points": db.child("users").child(token).child("points").get().val(),
                        "quizzes": db.child("users").child(token).child("quizzes").get().val()}
                db.child("users").child(token).set(data)

                session["game_room"] = game_room
                session["room_admin"] = True
                return redirect("/static/before_game")
            else:
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

            q1_num = "q" + str(get_random_int(subject))
            q2_num = "q" + str(get_random_int(subject))
            q3_num = "q" + str(get_random_int(subject))
            q4_num = "q" + str(get_random_int(subject))
            q5_num = "q" + str(get_random_int(subject))
            question1 = db.child("questions").child(subject).child(q1_num).child("question").get().val()
            question2 = db.child("questions").child(subject).child(q2_num).child("question").get().val()
            question3 = db.child("questions").child(subject).child(q3_num).child("question").get().val()
            question4 = db.child("questions").child(subject).child(q4_num).child("question").get().val()
            question5 = db.child("questions").child(subject).child(q5_num).child("question").get().val()
            answer1 = db.child("questions").child(subject).child(q1_num).child("answer").get().val()
            answer2 = db.child("questions").child(subject).child(q2_num).child("answer").get().val()
            answer3 = db.child("questions").child(subject).child(q3_num).child("answer").get().val()
            answer4 = db.child("questions").child(subject).child(q4_num).child("answer").get().val()
            answer5 = db.child("questions").child(subject).child(q5_num).child("answer").get().val()
            questions = {"subject": subject, "admin": token, "started": 0, "finished": 0, "question1": question1, "answer1": answer1, "question2": question2, "answer2": answer2, "question3": question3, "answer3": answer3, "question4": question4, "answer4": answer4, "question5": question5, "answer5": answer5, "best score": 1000, "best player": "none"}
            db.child("rooms").child(game_room).set(questions)

            data = {"email": email, "game room": game_room,
                    "points": db.child("users").child(token).child("points").get().val(),
                    "quizzes": db.child("users").child(token).child("quizzes").get().val()}
            db.child("users").child(token).set(data)

            session["game_room"] = game_room
            session["room_admin"] = True
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
            q1 = db.child("rooms").child(game_room).child("question1").get().val()
            q2 = db.child("rooms").child(game_room).child("question2").get().val()
            q3 = db.child("rooms").child(game_room).child("question3").get().val()
            q4 = db.child("rooms").child(game_room).child("question4").get().val()
            q5 = db.child("rooms").child(game_room).child("question5").get().val()

            if session.get("room_admin") == False:
                return render_template("static/game.html", email = session.get('email').split('@')[0], q1 = q1, q2 = q2, q3 = q3, q4 = q4, q5 = q5, game_room = session.get("game_room"))
            else:
                return render_template("static/game_hoster.html", email = session.get('email').split('@')[0], q1 = q1, q2 = q2, q3 = q3, q4 = q4, q5 = q5, game_room = session.get("game_room"))

        else:
            if session.get("room_admin") == False:
                q1_ans = request.form["q1_ans"]
                q2_ans = request.form["q2_ans"]
                q3_ans = request.form["q3_ans"]
                q4_ans = request.form["q4_ans"]
                q5_ans = request.form["q5_ans"]
            else:
                q1_ans = ""
                q2_ans = ""
                q3_ans = ""
                q4_ans = ""
                q5_ans = ""
            session["q1_ans"] = q1_ans
            session["q2_ans"] = q2_ans
            session["q3_ans"] = q3_ans
            session["q4_ans"] = q4_ans
            session["q5_ans"] = q5_ans
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
        q1_ans = session.get("q1_ans")
        q2_ans = session.get("q2_ans")
        q3_ans = session.get("q3_ans")
        q4_ans = session.get("q4_ans")
        q5_ans = session.get("q5_ans")
        if q1_ans == "":
            q1_ans = -1
        if q2_ans == "":
            q2_ans = -1
        if q3_ans == "":
            q3_ans = -1
        if q4_ans == "":
            q4_ans = -1
        if q5_ans == "":
            q5_ans = -1
        if int(db.child("rooms").child(game_room).child("answer1").get().val()) == int(
                q1_ans):
            countTrue += 1
        else:
            wrongAnswerTime += 7
        if int(db.child("rooms").child(game_room).child("answer2").get().val()) == int(
                q2_ans):
            countTrue += 1
        else:
            wrongAnswerTime += 7
        if int(db.child("rooms").child(game_room).child("answer3").get().val()) == int(
                q3_ans):
            countTrue += 1
        else:
            wrongAnswerTime += 7
        if int(db.child("rooms").child(game_room).child("answer4").get().val()) == int(
                q4_ans):
            countTrue += 1
        else:
            wrongAnswerTime += 7
        if int(db.child("rooms").child(game_room).child("answer5").get().val()) == int(
                q5_ans):
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

@app.route("/static/user_quizzes", methods=["POST", "GET"])
def user_quizzes():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            return render_template("static/user_quizzes.html", email=session.get('email').split('@')[0], token=session.get("token"))
        else:
            quiz_name = request.form["quiz_name"]
            if quiz_name == "create_new_quiz":
                return redirect("/static/create_quiz")
            else:
                return redirect("/static/main_create/" + quiz_name)


@app.route("/static/create_quiz", methods=["POST", "GET"])
def create_quiz():
    if session.get("logged_in") == None or session.get("logged_in") == False:
        return redirect("/static/login")
    else:
        if request.method == "GET":
            return render_template("static/create_quiz.html", email=session.get('email').split('@')[0], token=session.get("token"))
        else:
            quiz_name = request.form["quiz_name"]
            question1 = request.form["question1"]
            question2 = request.form["question2"]
            question3 = request.form["question3"]
            question4 = request.form["question4"]
            question5 = request.form["question5"]
            answer1 = request.form["answer1"]
            answer2 = request.form["answer2"]
            answer3 = request.form["answer3"]
            answer4 = request.form["answer4"]
            answer5 = request.form["answer5"]
            user_quizzes = db.child("users").child(session.get('token')).child("quizzes").get().val()
            db.child("questions").child(session.get("token")).child(quiz_name).child("q1").set({"question": question1, "answer": answer1})
            db.child("questions").child(session.get("token")).child(quiz_name).child("q2").set({"question": question2, "answer": answer2})
            db.child("questions").child(session.get("token")).child(quiz_name).child("q3").set({"question": question3, "answer": answer3})
            db.child("questions").child(session.get("token")).child(quiz_name).child("q4").set({"question": question4, "answer": answer4})
            db.child("questions").child(session.get("token")).child(quiz_name).child("q5").set({"question": question5, "answer": answer5})
            db.child("users").child(session.get("token")).update({"quizzes": user_quizzes + 1})
            return redirect("/static/user_quizzes")


@app.route("/android/login", methods=["POST", "GET"])
def android_login():
    email = request.form["email"]
    password = request.form["password"]
    checker = 0
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        checker = 1
    except:
        checker = 0
    if checker == 1:
        return "true"
    else:
        return "false"

@app.route("/android/join", methods=["POST", "GET"])
def android_join():
    email = request.form["email"]
    password = request.form["password"]
    token = auth.sign_in_with_email_and_password(email, password)["localId"]
    game_room = request.form["game_room"]
    if db.child("rooms").child(game_room).child("started").get().val() == 0:
        data = {"email": email, "game room": game_room,
                "points": db.child("users").child(token).child("points").get().val(),
                "quizzes": db.child("users").child(token).child("quizzes").get().val()}
        db.child("users").child(token).set(data)
        db.child("rooms").child(game_room).child("users_in").update({token: email.split('@')[0]})
        session["start_time"] = time.time()
        return "true"
    else:
        return "false"

@app.route("/android/game", methods=["POST", "GET"])
def android_game():
    game_room = request.form["game_room"]
    email = request.form["email"]
    password = request.form["password"]
    token = auth.sign_in_with_email_and_password(email, password)["localId"]
    end = time.time()
    countTrue = 0
    wrongAnswerTime = 0
    q1_ans = request.form["ans1"]
    q2_ans = request.form["ans2"]
    q3_ans = request.form["ans3"]
    q4_ans = request.form["ans4"]
    q5_ans = request.form["ans5"]
    if q1_ans == "":
        q1_ans = -1
    if q2_ans == "":
        q2_ans = -1
    if q3_ans == "":
        q3_ans = -1
    if q4_ans == "":
        q4_ans = -1
    if q5_ans == "":
        q5_ans = -1
    if int(db.child("rooms").child(game_room).child("answer1").get().val()) == int(
            q1_ans):
        countTrue += 2
    else:
        wrongAnswerTime += 1
    if int(db.child("rooms").child(game_room).child("answer2").get().val()) == int(
            q2_ans):
        countTrue += 2
    else:
        wrongAnswerTime += 1
    if int(db.child("rooms").child(game_room).child("answer3").get().val()) == int(
            q3_ans):
        countTrue += 2
    else:
        wrongAnswerTime += 1
    if int(db.child("rooms").child(game_room).child("answer4").get().val()) == int(
            q4_ans):
        countTrue += 2
    else:
        wrongAnswerTime += 1
    if int(db.child("rooms").child(game_room).child("answer5").get().val()) == int(
            q5_ans):
        countTrue += 2
    else:
        wrongAnswerTime += 1
    score = int(countTrue - wrongAnswerTime)
    if score < db.child("rooms").child(game_room).child("best score").get().val():
        db.child("rooms").child(game_room).child("best score").set(score)
        db.child("rooms").child(game_room).child("best player").set(token)
    return "response doesnt matters"


if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('server.crt', 'server.key')
    app.run(HOST, PORT)
    #app.run(HOST, PORT, ssl_context=context)