from flask import Flask, render_template

app = Flask(__name__)
app._static_folder = "static"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/travel")
def travel():
    return render_template("travel.html")