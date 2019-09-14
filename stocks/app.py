from json import load
from os import path, environ
from flask import Flask, render_template, request
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from stocks.scraper import Scraper
from stocks.util import AuthError

#pylint: disable=unused-argument
def strip_personal_info(event, hint):
    # Stripping username and password
    event['request']['data'].pop('username', None)
    event['request']['data'].pop('password', None)

    # if it fails during the scraper, there was a chance the payload sent to SMG
    # (containing username and password) would be sent (and we don't want that)
    for i in event['exception']['values']:
        i['stacktrace']['frames'] = \
            [destroyFormData(x) for x in i['stacktrace']['frames']]
    return event


def destroyFormData(data: dict) -> dict:
    # Delete username/password from variables
    data['vars'].pop('username', None)
    data['vars'].pop('password', None)

    # Search the payload for the accountnumber/password, and delete them if available
    if 'payload' in data['vars']:
        payload = data['vars']['payload']
        if 'ACCOUNTNO' in payload:
            data['vars']['payload'].pop('ACCOUNTNO')
        if 'USER_PIN' in payload:
            data['vars']['payload'].pop('USER_PIN')

    return data


# If a sentry URL exists, enable sentry error reporting
if environ.get('STOCKS_SENTRY_DSN'):
    sentry_sdk.init(
        before_send=strip_personal_info,
        dsn=environ.get('STOCKS_SENTRY_DSN'),
        integrations=[FlaskIntegration()]
    )

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


@app.route('/demo')
def demo():
    with open(path.join(currentDir, '../', 'demo.json')) as f:
        scraped_data = load(f)

    return render_template('index.html', data=scraped_data, highlight=highlight)


# for highlighting units
def highlight(unit: str) -> str:
    return 'negative' if unit.startswith("-") else 'positive'


if __name__ == '__main__':
    app.run()
