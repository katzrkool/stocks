from flask import Flask, render_template, redirect, url_for, request
from json import load
from os import path
from stocks.scraper import Scraper

app = Flask(__name__, static_url_path='/static', static_folder='../static/',
            template_folder='../templates')
currentDir = path.dirname(path.realpath(__file__))


@app.route('/')
def index():
    with open(path.join(currentDir, '../', 'data.json'), 'r') as f:
        data = load(f)
    return render_template('index.html', data=data, highlight=highlight)


@app.route('/scrape', methods=['POST'])
def scrape():
    s = Scraper(request.form['username'], request.form['password'])
    s.go()
    return '200 OK'


# for highlighting units
def highlight(unit: str) -> str:
    return 'negative' if unit.startswith("-") else 'positive'


if __name__ == '__main__':
    app.run()
