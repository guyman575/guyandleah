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
app.secret_key = 'butts'
Mobility(app)
credentials_dict = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
credential = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict,
    ["https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credential)

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
    session['not_found'] = False
    if session.get('reservation'):
        session.pop('reservation')

    if flask.request.method == 'POST':
        rsvps = []
        for i in range(2):
            if request.form.get(f"attending_{i}"):
                rsvps.append(Rsvp.from_form(request.form,i))
        makeRsvp(rsvps)
    return render_template("rsvp.html")

@app.route("/reservation", methods=['POST'])
def reservation():
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
    return render_template("rsvp.html")

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