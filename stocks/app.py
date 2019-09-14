from os import path
from flask import Flask, render_template, request
from stocks.scraper import Scraper
from stocks.util import AuthError

app = Flask(__name__, static_url_path='/static', static_folder='../static/',
            template_folder='../templates')
currentDir = path.dirname(path.realpath(__file__))

# Below are the API endpoints
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            s = Scraper(request.form['username'], request.form['password'])
            scraped_data = s.scrape()
            return render_template('index.html', data=scraped_data, highlight=highlight)
        except AuthError:
            return 'Incorrect Username or Password', 403

    return render_template('login.html')


# for highlighting units
def highlight(unit: str) -> str:
    return 'negative' if unit.startswith("-") else 'positive'


if __name__ == '__main__':
    app.run()
