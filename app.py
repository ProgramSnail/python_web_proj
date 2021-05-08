from flask import Flask, render_template

app = Flask("App")

@app.route("/")
def index():
    return render_template("index.html")