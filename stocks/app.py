from flask import Flask, render_template, request, redirect, url_for, make_response
from json import load
from os import path, stat
from stocks.scraper import Scraper
from socket import gethostbyname
from random import choice
from string import ascii_lowercase

app = Flask(__name__, static_url_path='/static', static_folder='../static/',
            template_folder='../templates')
currentDir = path.dirname(path.realpath(__file__))
serverIP = None
securityCookie = None
filename = 'code.txt'


@app.before_first_request
def findIP():
    global serverIP
    serverIP = gethostbyname('lkellar.org')


@app.route('/')
def index():
    if not security():
        return f'Submit a POST request to <a href={url_for("verify")}>/verify</a> with param "security"= the contents of {filename}'

    with open(path.join(currentDir, '../', 'data.json'), 'r') as f:
        data = load(f)
    return render_template('index.html', data=data, highlight=highlight)


@app.route('/scrape', methods=['POST'])
def scrape():
    s = Scraper(request.form['username'], request.form['password'])
    s.go()
    return '200 OK'


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'GET':
        return app.send_static_file('cookie.html')
    if request.form['secret'] == fetchSecurityCookie():
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('security', fetchSecurityCookie(), expires=1703716200, secure=True)
        return resp
    else:
        return 'INVALID COOKIE!'


def fetchSecurityCookie() -> str:
    global securityCookie
    if not securityCookie:
        with open(path.join(currentDir, '../', filename), 'r') as f:
            securityCookie = f.read()

    return securityCookie


def security() -> bool:
    if request.remote_addr == serverIP or request.remote_addr == '127.0.0.1':
        return True
    if not stat(path.join(currentDir, '../', filename)).st_size == 0:
        with open(path.join(currentDir, '../', filename), 'w') as f:
            f.write(randomword(20))

    if request.cookies.get('security'):
        if request.cookies.get('security') == fetchSecurityCookie():
            return True
    else:
        return False


def randomword(length):
    return ''.join(choice(ascii_lowercase) for i in range(length))


# for highlighting units
def highlight(unit: str) -> str:
    return 'negative' if unit.startswith("-") else 'positive'


if __name__ == '__main__':
    app.run()
