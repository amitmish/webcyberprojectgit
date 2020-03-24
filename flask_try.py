from flask import Flask, redirect, url_for, render_template, request
app = Flask(__name__, template_folder='')

@app.route("/")
def home():
    return render_template("index.html")

email = ""
password = ""
@app.route("/static/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        return redirect("/{0}".format(user))
        #return redirect(url_for("user", usr=user))
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='12345')