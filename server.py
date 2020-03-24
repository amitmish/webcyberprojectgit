import socket
import sys
import pyrebase
from thread import *
from server_functions import *
from easygui import *
import random
import time
import tkinter as tk
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



HOST = '127.0.0.1'  # Symbolic name meaning all available interfaces
PORT = 10000  # Arbitrary non-privileged port

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
    conn.send('Welcome to the server.\n')  # send only takes string

    # infinite loop so that function do not terminate and thread do not end.
    while True:

        # Receiving from client
        game_room = 0
        client_info = conn.recv(1024)
        print client_info
        command = client_info.split("*")[0]
        email = client_info.split("*")[1]
        password = client_info.split("*")[2]
        token = ""
        if command == "Sign In":
            checker = 0
            while checker != 1:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    checker = 1
                except:
                    checker = 0
                if checker == 1:
                    conn.sendall("true")
                    token = user["localId"]
                else:
                    conn.sendall("false")
                    client_info = conn.recv(1024)
                    command = client_info.split("*")[0]
                    email = client_info.split("*")[1]
                    password = client_info.split("*")[2]
        elif command == "Sign Up":
            checker = 0
            while checker != 1:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    checker = 1
                except:
                    checker = 0
                if checker == 1:
                    conn.sendall("true")
                    user = auth.sign_in_with_email_and_password(email, password)
                    token = user["localId"]
                    data = {"email": email, "game room": "none", "points": 0}
                    db.child("users").child(token).set(data)
                else:
                    conn.sendall("false")
                    client_info = conn.recv(1024)
                    command = client_info.split("*")[0]
                    email = client_info.split("*")[1]
                    password = client_info.split("*")[2]
        elif command == "Reset Password":
            checker = 0
            while checker != 1:
                try:
                    auth.send_password_reset_email(email)
                    checker = 1
                except:
                    checker = 0
                if checker == 1:
                    conn.sendall("true")
                else:
                    conn.sendall("false")
                    client_info = conn.recv(1024)
                    print client_info.split("*")[1]
                    command = client_info.split("*")[0]
                    email = client_info.split("*")[1]
        is_admin = conn.recv(1024)
        if is_admin == "admin":
            result = ""
            all_users = db.child("users").get()
            for user in all_users.each():
                token = user.key()
                email = db.child("users").child(token).child("email").get().val()
                game_room = db.child("users").child(token).child("game room").get().val()
                points = db.child("users").child(token).child("points").get().val()
                result += "User Token: " + str(token) + "\nEmail: " + str(email) + "\nCurrent Game Room: " + str(
                    game_room) + "\npoints: " + str(points)
            conn.sendall(result)
        else:
            conn.sendall(email)

            client_info = conn.recv(1024)
            command = client_info.split("*")[0]
            game_room = int(client_info.split("*")[1])
            if command == "Create":
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
                questions = {"admin": token, "started": 0, "finished": 0, "q1": get_random_int(),
                             "q2": get_random_int(),
                             "q3": get_random_int(),
                             "best score": 1000, "best player": "none"}
                db.child("rooms").child(game_room).set(questions)
                print "game pin: " + str(game_room)
                conn.sendall(str(game_room))
                is_started = conn.recv(1024)
                t = threading.Thread(target=open_room, args=(game_room,))
                if is_started == "started":
                    t.start()
            elif command == "Join":
                checker = 0
                while checker != 1:
                    if db.child("rooms").child(game_room).child("started").get().val() == 0:
                        data = {"email": email, "game room": game_room,
                                "points": db.child("users").child(token).child("points").get().val()}
                        db.child(token).set(data)
                        checker = 1
                        conn.sendall("true")
                    else:
                        checker = 0
                        conn.sendall("false")
                        client_info = conn.recv(1024)
                        command = client_info.split("*")[0]
                        game_room = int(client_info.split("*")[1])
                wait_for_start(game_room)
            winnerName = the_game(email, token, game_room)
            conn.sendall(winnerName)

    # came out of loop
    conn.close()


# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread, (conn,))

s.close()