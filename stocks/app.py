from flask import Flask, render_template, request, redirect, url_for, make_response
from json import load
from os import path
from stocks.scraper import Scraper
from random import choice
from string import ascii_lowercase

app = Flask(__name__, static_url_path='/static', static_folder='../static/',
            template_folder='../templates')
currentDir = path.dirname(path.realpath(__file__))
serverIP = None
securityCookie = None
filename = 'code.txt'

# Below are the API endpoints
@app.route('/')
def index():
    if not authenticate():
        return f'Submit a POST request to <a href={url_for("verify")}>/verify</a> with param "stocks_security"= the contents of {filename}'

    with open(path.join(currentDir, '../', 'data.json'), 'r') as f:
        data = load(f)
    return render_template('index.html', data=data, highlight=highlight)


@app.route('/scrape', methods=['POST'])
def scrape():
    if authenticate():
        s = Scraper(request.form['username'], request.form['password'])
        s.go()
        return '200 OK'
    return '403 NO', 403


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'GET':
        return app.send_static_file('cookie.html')
    if request.form['secret'] == fetchSecurityCookie():
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('stocks_security', fetchSecurityCookie(), expires=1703716200, secure=True)
        return resp
    else:
        return 'INVALID COOKIE!'


@app.route('/reset')
def reset():
    if authenticate():
        generateCookie()
        return '200 OK'
    return '403 NO', 403


# Below are helper functions for endpoints
def fetchSecurityCookie() -> str:
    global securityCookie
    if not securityCookie:
        with open(path.join(currentDir, '../', filename), 'r') as f:
            securityCookie = f.read()

    return securityCookie


def generateCookie():
    with open(path.join(currentDir, '../', filename), 'w') as f:
        f.write(randomword(20))

    fetchSecurityCookie()


def authenticate() -> bool:
    if request.remote_addr in ['127.0.0.1', '192.168.0.1']:
        return True
    if not path.exists(path.join(currentDir, '../', filename)):
        generateCookie()

    if request.cookies.get('stocks_security'):
        if request.cookies.get('stocks_security') == fetchSecurityCookie():
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
