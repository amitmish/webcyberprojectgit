import pyrebase
import time
import tkinter as tk
import random
from easygui import *

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


def get_random_int():
    return random.randint(1, 100)

def open_room(game_room):
    seconds = 15
    while seconds > 0:
        db.child("rooms").child(game_room).update({"timer": seconds})
        time.sleep(1)
        seconds = seconds - 1
    db.child("rooms").child(game_room).update({"finished": 1})
    seconds = 15
    while seconds > 0:
        db.child("rooms").child(game_room).update({"finished_timer": seconds})
        time.sleep(1)
        seconds = seconds - 1
    db.child("rooms").child(game_room).remove()

def wait_for_start(game_room):
    def task():
        while db.child("rooms").child(game_room).child("started").get().val() == 0:
            time.sleep(3)
        else:
            root.destroy()
    root = tk.Tk()
    root.title("Example")

    label = tk.Label(root, text="Waiting for room manager to start")
    label.pack()

    root.after(200, task)
    root.mainloop()

def finished(game_room):
    def task():
        while db.child("rooms").child(game_room).child("finished").get().val() == 0:
            time.sleep(3)
        else:
            root.destroy()


    root = tk.Tk()
    root.title("Example")

    label = tk.Label(root, text="Nice Job!\nWait for game to finish")
    label.pack()

    root.after(200, task)
    root.mainloop()

def check_admin(email, password):
    if email == "admin" and password == "admin":
        return True
    else:
        return False

def the_game(email, token, game_room):
    number_of_question_1 = db.child("rooms").child(game_room).child("q1").get().val()
    number_of_question_2 = db.child("rooms").child(game_room).child("q2").get().val()
    number_of_question_3 = db.child("rooms").child(game_room).child("q3").get().val()
    msg = "Answer the questions"
    title = "CyberProject"
    countTrue = 0
    wrongAnswerTime = 0
    start = time.time()
    fieldNames = [db.child("questions").child("q" + str(number_of_question_1)).child("question").get().val(),
                  db.child("questions").child("q" + str(number_of_question_2)).child("question").get().val(),
                  db.child("questions").child("q" + str(number_of_question_3)).child(
                      "question").get().val()]  # we start with blanks for the values
    fieldValues = multenterbox(msg, title, fieldNames)
    end = time.time()
    print fieldValues[0]
    if str(fieldValues[0]) == "":
        fieldValues[0] = -1
    if str(fieldValues[1]) == "":
        fieldValues[1] = -1
    if str(fieldValues[2]) == "":
        fieldValues[2] = -1
    if int(db.child("questions").child("q" + str(number_of_question_1)).child("answer").get().val()) == int(
            fieldValues[0]):
        countTrue += 1
    else:
        wrongAnswerTime += 7
    if int(db.child("questions").child("q" + str(number_of_question_2)).child("answer").get().val()) == int(
            fieldValues[1]):
        countTrue += 1
    else:
        wrongAnswerTime += 7
    if int(db.child("questions").child("q" + str(number_of_question_3)).child("answer").get().val()) == int(
            fieldValues[2]):
        countTrue += 1
    else:
        wrongAnswerTime += 7
    score = int(end - start + wrongAnswerTime) - int(countTrue)
    finished(game_room)
    winnerName = ""
    db.child("rooms").child(game_room).child(token).set({"score": score})
    if score < db.child("rooms").child(game_room).child("best score").get().val():
        db.child("rooms").child(game_room).child("best score").set(score)
        db.child("rooms").child(game_room).child("best player").set(token)
        winnerPoints = db.child("users").child(token).child("points").get().val()
        db.child("users").child(token).update({"points": winnerPoints + 1})
        winnerName = email
    return winnerName.split("@")[0]