from flask import Flask, render_template
from flask_mobility import Mobility

app = Flask(__name__)
app._static_folder = "static"
Mobility(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/travel")
def travel():
    return render_template("travel.html")