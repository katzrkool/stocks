from datetime import date, timedelta
from json import load
from os import path
from flask import Flask, render_template, request, jsonify
import requests
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from stocks.scraper import Scraper
from stocks.util import AuthError, AlphaVantageError, Analyzer


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

current_dir = path.dirname(path.realpath(__file__))

with open(path.join(current_dir, '../', 'config.json'), 'r') as f:
    config = load(f)

# If a sentry URL exists, enable sentry error reporting
if 'sentry_dsn' in config:
    sentry_sdk.init(
        before_send=strip_personal_info,
        dsn=config['sentry_dsn'],
        integrations=[FlaskIntegration()]
    )

app = Flask(__name__, static_url_path='/static', static_folder='../static/',
            template_folder='../templates')

# Loads an Analyzer with the SEC fee from config and makes it globally available
analyzer = Analyzer(config['sec_fee_per_dollar'])


# Below are the API endpoints
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            s = Scraper(request.form['username'], request.form['password'], analyzer)
            scraped_data = s.scrape()
            return render_template('index.html', data=scraped_data, highlight=highlight,
                                   calculate_fees=analyzer.calculate_fees,
                                   most_recent_close_time=most_recent_close_time,
                                   sec_fee=config['sec_fee_per_dollar'],
                                   bool=bool)
        except AuthError:
            return 'Incorrect Username or Password', 403

    return render_template('login.html')


@app.route('/price')
def fetch_stock_price():
    '''
    Takes a ticker and hits the Alpha Vantage api to get the current price and returns it
    '''
    ticker = request.args.get('ticker')
    params = {'function': 'GLOBAL_QUOTE', 'symbol': ticker, 'apikey': config['api_key']}
    response = requests.get('https://www.alphavantage.co/query', params=params).json()

    # if the information we were looking for appears, that's great!, return it
    if 'Global Quote' in response:
        return jsonify({'price': response['Global Quote']['05. price']})

    # If we hit our API Key limit, return error message
    if 'Note' in response:
        return jsonify({'error': 'API Key hit rate limit, try again in 60 seconds'}), 503

    # If neither of those things happen, something went wrong
    raise AlphaVantageError()

@app.route('/demo')
def demo():
    with open(path.join(current_dir, '../', 'demo.json')) as f:
        scraped_data = load(f)

    return render_template('index.html', data=scraped_data, highlight=highlight,
                           calculate_fees=analyzer.calculate_fees,
                           most_recent_close_time=most_recent_close_time,
                           sec_fee=config['sec_fee_per_dollar'],
                           bool=bool)


# for highlighting units
def highlight(unit: str) -> str:
    return 'negative' if unit.startswith("-") else 'positive'

# for getting the most recent close date/time
def most_recent_close_time() -> str:
    now = date.today()
    offset = 1
    if now.weekday() == 6:
        offset = 2
    elif now.weekday() == 0:
        offset = 3

    close_date = now - timedelta(days=offset)

    return f'{close_date.strftime("%m/%d/%Y")} 4:00 PM EST'

if __name__ == '__main__':
    app.run()
