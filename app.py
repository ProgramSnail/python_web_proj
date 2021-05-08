import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask("App")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////" + \
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "SAFmdsdDkSukyuDd"
db = SQLAlchemy(app)

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        session["user_name"] = name
        session["user_password"] = password
        return redirect(url_for("user_page", user_name=name))
    else:
        if "user_name" in session:
            return redirect(url_for("user_page", user_name=session["user_name"]))
        return render_template("login.html")


@app.route("/<user_name>")
def user_page(user_name):
    if not "user_name" in session:
        return redirect(url_for("login"))
    return render_template("user_page.html")