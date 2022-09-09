from flask import Flask, render_template, request, redirect
from flask_mobility import Mobility

app = Flask(__name__)
app._static_folder = "static"
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

if __name__ == '__main__':
    app.run(host='localhost', port=8000)