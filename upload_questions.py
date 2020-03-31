import pyrebase
import random
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
db = firebase.database()
data = {"question": "What is the highest points total (as of 2018-19) in a season for a team in the English Premier League?", "answer": 100}
db.child("questions").child("sports").child("q3").set(data)