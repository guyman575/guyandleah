import flask
import gspread
import json
import os
import re

from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from flask_mobility import Mobility
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)
app._static_folder = "static"
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
Mobility(app)
credentials_dict = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
credential = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict,
    ["https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credential)
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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route("/auth",methods=['GET', 'POST'])
def auth():
    if flask.request.method == 'GET':
        return render_template("auth.html")
    else:
        passphrase_entered = request.form.get("passphrase")
        print(passphrase_entered)
        if passphrase_entered == PASSPHRASE:
            session['authenticated'] = True
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
        makeRsvp(rsvps)
        session.pop('reservation', None)
        session.pop('not_found', None)
    return render_template("rsvp.html")

@app.route("/reservation", methods=['POST'])
def reservation():
    if not session.get('authenticated'):
        return redirect(url_for('auth'))
    # Sanitize input so dumb friends cant code inject us
    input_name = re.sub(r'[^a-zA-Z\s]', '',request.form.get('name'))
    print(input_name)
    reservations = getReservationData(input_name)
    print(reservations)
    if reservations:
        session['reservation'] = reservations
        session['not_found'] = False
    else:
        session['not_found'] = True
        session.pop('reservation', None)
    return redirect(url_for('rsvp'))

def getReservationData(name):
    reservations_db_sheet = client.open_by_key('14Je37BKWxVVIXHfiMnGu37m_0KI9pKyept4ZOVotWW8').worksheet("reservations")
    all_reservations = reservations_db_sheet.get_all_records()
    print(all_reservations)
    invite_id = 0
    for reservation in all_reservations:
        if reservation['name'].lower() == name.lower():
            invite_id = reservation['invite_id']
    
    matching_reservations = [res for res in all_reservations if res['invite_id'] == invite_id]
    return matching_reservations

class Rsvp:
    def __init__(self,name,invite_id,attending,rehearsal_attending, food):
        self.name = name
        self.invite_id = invite_id
        self.attending = attending
        self.rehearsal_attending = rehearsal_attending
        self.food = food

    @classmethod
    def from_form(cls,form,index):
        name = form.get(f"rsvp_name_{index}")
        id = form.get(f"rsvp_id_{index}")
        attending = form.get(f"attending_{index}")
        rehearsal = form.get(f"rehearsal_{index}")
        food = form.get(f"food_pref_{index}")
        return Rsvp(name,id,attending,rehearsal,food)

        

def makeRsvp(rsvps):
    rsvp_sheet = client.open_by_key('14Je37BKWxVVIXHfiMnGu37m_0KI9pKyept4ZOVotWW8').worksheet("RSVPs")
    values = [[rsvp.name, rsvp.invite_id, rsvp.attending, rsvp.rehearsal_attending, rsvp.food] for rsvp in rsvps]
    rsvp_sheet.append_rows(values,insert_data_option='INSERT_ROWS')


if __name__ == '__main__':
    app.run(host='localhost', port=8000)