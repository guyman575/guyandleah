from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from flask_mobility import Mobility
import flask

app = Flask(__name__)
app._static_folder = "static"
app.secret_key = 'butts'
Mobility(app)

@app.before_request
def before_request():
    if app.debug or \
        request.is_secure or \
        request.url_root.startswith('http://127.0.0.1') or \
        request.url_root.startswith('http://localhost'):
        return
    url = request.url.replace('http://', 'https://', 1)
    code = 301
    return redirect(url, code=code)

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

@app.route("/registry")
def registry():
    return render_template("registry.html")

@app.route("/rsvp", methods=['GET', 'POST'])
def rsvp():
    if session.get('reservation'):
        session.pop('reservation')
    return render_template("rsvp.html")

@app.route("/reservation", methods=['POST'])
def reservation():

    reservation = {'attendees': [
        {'name': 'John Doe', 'rehearsal': True},
        {'name': 'Jane Doe', 'rehearsal': False}
    ]}
    session['reservation'] = reservation
    return render_template("rsvp.html")

if __name__ == '__main__':
    app.run(host='localhost', port=8000)