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

@app.route("/thingstodo")
def thingstodo():
    return render_template("thingstodo.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

if __name__ == '__main__':
    app.run(host='localhost', port=9874)