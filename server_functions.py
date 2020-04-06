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


def get_random_int(subject):
    return random.randint(1, len(db.child("questions").child(subject).get().each()))

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

def check_admin(email, password):
    if email == "admin" and password == "admin":
        return True
    else:
        return False

def add_question_to_db(question, answer, subject):
    questions_num = len(db.child("questions").child(subject).get().each())
    db.child("questions").child(subject).child("q" + str(questions_num + 1)).set({"question": question, "answer": int(answer)})