from flask import Flask, render_template

app = Flask(__name__)
app._static_folder = "static"

@app.route("/")
def home():
    return render_template("home.html")