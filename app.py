import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask("App")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////" + \
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "SAFmdsdDkSukyuDd"
db = SQLAlchemy(app)

MAX_NAME_LENGTH = 30
MAX_PASSWORD_LENGTH = 30
MAX_PARAM_LENGTH = 30
NONE_VALUE = "None"


class UserData(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True, nullable=False)
    password = db.Column(db.String(MAX_PASSWORD_LENGTH), nullable=False)
    interest1 = db.Column(db.String(MAX_PARAM_LENGTH), nullable=False)
    interest2 = db.Column(db.String(MAX_PARAM_LENGTH), nullable=False)
    interest3 = db.Column(db.String(MAX_PARAM_LENGTH), nullable=False)
    usr_lang = db.Column(db.String(MAX_PARAM_LENGTH), nullable=False)
    foreign_lang = db.Column(db.String(MAX_PARAM_LENGTH), nullable=False)
    # add password hash instead of password

db.create_all()


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        if UserData.query.filter_by(name=name).count() == 0:
            db.session.add(UserData(name=name, password=password,
                interest1=NONE_VALUE, interest2=NONE_VALUE, interest3=NONE_VALUE, 
                usr_lang=NONE_VALUE, foreign_lang=NONE_VALUE))
            db.session.commit()
            print("Added user " + name)
        elif UserData.query.filter_by(name=name).first().password != password:
            print("Wrong password") # later - popup
            return render_template("login.html", form_msg="Wrong password")
        session["user_name"] = name
        session["user_password"] = password
        if len(name) >= MAX_NAME_LENGTH and len(password) >= MAX_PASSWORD_LENGTH:
            print("Too long name / password") # later - popup
            return render_template("login.html", form_msg="Too long name / password")
        return redirect(url_for("user_page", user_name=name))
    else:
        if "user_name" in session:
            return redirect(url_for("user_page", user_name=session["user_name"]))
        return render_template("login.html")


def create_interests_list(usr):
    a = []
    if usr.interest1 != NONE_VALUE:
        a.append(usr.interest1)
    if usr.interest2 != NONE_VALUE:
        a.append(usr.interest2)
    if usr.interest3 != NONE_VALUE:
        a.append(usr.interest3)
    return a


def get_matching_users(usr):
    users = []
    if usr.usr_lang != NONE_VALUE and usr.foreign_lang != NONE_VALUE:
        users = UserData.query.filter_by(usr_lang=usr.foreign_lang) \
            .filter_by(foreign_lang=usr.usr_lang).all()
    else:
        users = UserData.query.all()
    matching_list = []
    a = create_interests_list(usr)
    for user in users:
        if user == usr:
            continue
        b = create_interests_list(user)
        match = False
        same_interest = ""
        for x in a:
            for y in b:
                if x == y:
                    match = True
                    same_interest = x
                    break
            if match:
                break
        if match:
            matching_list.append([user.name, same_interest])
    return matching_list

@app.route("/<user_name>", methods=["GET", "POST"])
def user_page(user_name):
    if not "user_name" in session:
        return redirect(url_for("login"))
    usr = UserData.query.filter_by(name=user_name).first()
    form_msg = ""
    if request.method == "POST":
        param_str = request.form["param-str"]
        if len(param_str) >= MAX_PARAM_LENGTH:
            print("Too long text")
            form_msg = "Too long text"
        elif len(param_str) == 0:
            print("No text")
            form_msg = "No text"
        else:
            param_id = request.form["param-id"]
            if param_id == "i1":
                usr.interest1 = param_str
            elif param_id == "i2":
                usr.interest2 = param_str
            elif param_id == "i3":
                usr.interest3 = param_str
            elif param_id == "usr-lang":
                usr.usr_lang = param_str
            elif param_id == "foreign-lang":
                usr.foreign_lang = param_str
            db.session.commit()
            return redirect(url_for("user_page", user_name=user_name))
    return render_template("user_page.html", user_name=user_name,
        interest1=usr.interest1, interest2=usr.interest2,
        interest3=usr.interest3, form_msg=form_msg,
        user_language=usr.usr_lang, foreign_language=usr.foreign_lang, 
        matching_users=get_matching_users(usr)) # not efficient