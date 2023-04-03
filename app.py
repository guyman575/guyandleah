import flask
import json
import os
import re

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mobility import Mobility
from util.rsvp import Rsvp
from util.sheet_service import SheetService


app = Flask(__name__)
app._static_folder = "static"
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
Mobility(app)

SHEET_SERVICE = SheetService(
    json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')),
    os.environ.get('GOOGLE_SPREADSHEET_ID'))
PASSPHRASE = os.environ.get('WEDDING_PASSPHRASE')

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

# Hidden route used for debugging purposes to make it easy to clear session cookies
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))


# Authentication required only for RSVP page, redirects to rsvp page on success
@app.route("/auth",methods=['GET', 'POST'])
def auth():
    if flask.request.method == 'GET':
        return render_template("auth.html")
    else:
        passphrase_entered = re.sub(r'[^a-zA-Z\s0-9]', '',request.form.get("passphrase")) 
        if passphrase_entered == PASSPHRASE:
            session['authenticated'] = True
            session['failed_pass_attempts'] = 0
            return redirect(url_for('rsvp'))
        else:
            if not session.get('failed_pass_attempts'):
                session['failed_pass_attempts'] = 0
            session['failed_pass_attempts'] += 1
            return render_template("auth.html")


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
    if not session.get('authenticated'):
        return redirect(url_for('auth'))

    if flask.request.method == 'POST':
        rsvps = []
        for i in range(2):
            if request.form.get(f"attending_{i}"):
                rsvps.append(Rsvp.from_form(request.form,i))
        SHEET_SERVICE.makeRsvp(rsvps)
        session.pop('reservation', None)
        session.pop('not_found', None)
    return render_template("rsvp.html")

@app.route("/reservation", methods=['POST'])
def reservation():
    if not session.get('authenticated'):
        return redirect(url_for('auth'))
    # Sanitize input so dumb friends cant code inject us
    input_name = re.sub(r'[^a-zA-Z\s]', '',request.form.get('name'))
    reservations = SHEET_SERVICE.getReservationData(input_name)
    if reservations:
        session['reservation'] = reservations
        session['not_found'] = False
        session['requested_user'] = input_name
    else:
        session['not_found'] = True
        session.pop('reservation', None)
    return redirect(url_for('rsvp'))

@app.route("/resetrsvp", methods=['POST'])
def resetrsvp():
    session.pop('reservation', None)
    session.pop('not_found', None)
    session.pop('requested_user', None)
    return redirect(url_for('rsvp'))

if __name__ == '__main__':
    app.run(host='localhost', port=8000)