import flask
import json
import os
import re

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

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

# @app.route("/rsvp2")
# def rsvp2():
#     return render_template("rsvp2.html")

@app.route("/rsvp", methods=['GET', 'POST'])
def rsvp():
    if not session.get('authenticated'):
        return redirect(url_for('auth'))

    if flask.request.method == 'POST':
        rsvps = []
        for i in range(10):
            if request.form.get(f"attending_{i}"):
                rsvps.append(Rsvp.from_form(request.form,i))
            else:
                break
        SHEET_SERVICE.makeRsvp(rsvps)
        session.pop('reservation', None)
        session.pop('not_found', None)
        session.pop('requested_user', None)
        return redirect(url_for('sendit'))

    return render_template("rsvp.html")

@app.route("/reservation", methods=['POST'])
def reservation():
    if not session.get('authenticated'):
        return redirect(url_for('auth'))
    # Sanitize input so dumb friends cant code inject us
    input_name = re.sub(r'[^a-zA-Z\s-]', '',request.form.get('name'))
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

@app.route("/sendit")
def sendit():
    return render_template("sendit.html")

# @app.route("/api/v1/res/<name>", methods=['GET'])
# def v1res(name):
#     if not session.get('authenticated'):
#         return redirect(url_for('auth'))
#     input_name = re.sub(r'[^a-zA-Z\s-]', '',name)
#     if flask.request.method == 'GET':
#         reservations = SHEET_SERVICE.getReservationData(input_name)
#         print(reservations)
#         return jsonify({'reservations':reservations, 'sanitized_name': input_name})

# @app.route("/api/v1/rsvp", methods=['POST'])
# def v1rsvp():
#     if not session.get('authenticated') and not is_local(app,request):
#         return redirect(url_for('auth'))
#     if flask.request.method == 'POST':
#         request_data = request.get_json()
#         rsvps = [Rsvp.from_json(blob) for blob in request_data['rsvps']]
#         SHEET_SERVICE.makeRsvp(rsvps)
#         return jsonify({})

# @app.route("/api/v1/auth", methods=['POST'])
# def v1auth():
#     passphrase_entered = re.sub(r'[^a-zA-Z\s0-9]', '',request.get_json()['passphrase']) 
#     if passphrase_entered == PASSPHRASE:
#         session['authenticated'] = True
#         session['failed_pass_attempts'] = 0
#         return jsonify({"authenticated": True})
#     else:
#         if not session.get('failed_pass_attempts'):
#             session['failed_pass_attempts'] = 0
#         session['failed_pass_attempts'] += 1
#         return jsonify({"authenticated": False})



        
def is_local(app, request):
    return app.debug or \
        request.url_root.startswith('http://127.0.0.1') or \
        request.url_root.startswith('http://localhost')

if __name__ == '__main__':
    app.run(host='localhost', port=8000)