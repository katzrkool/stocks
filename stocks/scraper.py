from time import time
from datetime import datetime, timedelta

import requests
import xmltodict
from stocks.util import AuthError


class Scraper:
    def __init__(self, username: str, password: str, analyzer):
        self.username = username
        self.password = password
        self.analyzer = analyzer
        self.s = requests.session()

    def scrape(self) -> dict:
        '''
        The main scraping class of Scraper. Call this class to initiate the scraping

        returns: a dict with formatted scrape data
        '''
        # login and authenticate
        self.login(self.username, self.password)

        # get the summary and stock holdings
        summary = self.get_summary()
        summary = self.format_summary_values(summary)
        holdings = self.get_holdings()

        data = {**holdings, **summary}

        data['gainslosses'] = self.get_realized_gains()
        data['recent'] = self.get_transactions()
        data['analytics'] = self.analyzer.analyze(data)

        return data

    def login(self, username: str, password: str):
        '''
        Login to stock market game and authenticate

        username: str, the username for the stockmarketgame account to login to
        password: str, the password for the account
        '''
        self.s.get('https://www.stockmarketgame.org/login.html')

        # For some reason, we've gotta hit this page with the current unix time stamp to login
        query = {'tpl': 'xmltpl/pingxml', '_': self.unix_stamp()}
        self.s.get('https://www.stockmarketgame.org/cgi-bin/haipage/page.html', params=query)

        # Now, we load in our username/password, and leave security string blank
        payload = {'ACCOUNTNO': username,
                   'USER_PIN': password,
                   'SECURITY_STRING': ''}
        r = self.s.post('https://www.stockmarketgame.org/cgi-bin/hailogin', data=payload)

        # If the site says invalid user id, we also say invalid user id
        if 'invalid User ID' in r.text:
            raise AuthError()

    @staticmethod
    def unix_stamp()-> str:
        '''
        Returns a unix time stamp
        '''
        return str(round(time()))

    def get_transactions(self) -> list:
        '''
        Hits the SMG api and returns a list of transactions
        '''
        data = self.fetch_xml('Administration/game/a_trad/cont_transnotes')
        if data['transactions']:
            record = data['transactions']['record']
            return [record] if isinstance(record, dict) else record

        return []

    def fetch_xml(self, url: str) -> dict:
        '''
        Helper function, takes a url that returns in xml format, parses it to dict,
             and returns a dict
        '''
        query = {'tpl': url,
                 '_': self.unix_stamp()}
        data = self.s.get(
            'https://www.stockmarketgame.org/cgi-bin/haipage/page.html',
            params=query).text

        # cut out everything before the xml tag
        data = '<xml id="xmlDataIsland">' + \
               data.split('<xml id="xmlDataIsland">')[1]
        data = data.split('</xml>')[0] + '</xml>'

        # return a parsed dict
        return dict(xmltodict.parse(data)['xml']['response'])

    def get_summary(self) -> dict:
        # Gets a summary of a users's portfoilo and returns a dict
        today = datetime.today()
        query = {'tpl': 'Administration/game/a_trad/pa_xml',
                 'fromdate': (today - timedelta(days=4)).strftime('%-m/%-d/%Y'),
                 'todate': today.strftime('%-m/%-d/%Y'),
                 'ticks': 'DAILY',
                 '_': self.unix_stamp()}

        # this returns some xml, but I'm converting it to a dict because xml is no fun
        data = self.s.get('https://www.stockmarketgame.org/cgi-bin/haipage', params=query).text

        # also, they return non-valid xml so we must fix it
        data = data.replace('</html>', '</HTML>').replace('S&P500', 'S&amp;P500')
        data = dict(xmltodict.parse(data)['HTML']['xml']['response'])
        if int(data['dataresult']['noofrecords']) > 1:
            data['dataresult']['record'] = data['dataresult']['record'][-1]

        return data

    def get_holdings(self) -> dict:
        # Hit and return from the account holdings page
        data = self.fetch_xml('Administration/game/a_trad/cont_acctholdings')
        if data['transactions']:
            record = data['transactions']['record']

            # if the record is a single item, put it in a list
            record = [record] if not isinstance(record, list) else record

            # format each stock value
            data['transactions']['record'] = [self.format_stock_values(i) for i in record]
            return data

        return {}

    def get_realized_gains(self) -> list:
        # Hit and return from the realized gains/losses section
        data = self.fetch_xml('Administration/game/a_trad/cont_gainsloss')

        data.pop('account_info')
        if data['transactions']:
            data = data['transactions']['record']
            data = [data] if isinstance(data, dict) else data

            return [self.format_realized_values(i) for i in data]
        return []

    @staticmethod
    def format_realized_values(stock: dict) -> dict:
        # Formats the data from the realized values api
        for i in ['netcostpershare', 'netsalepershare', 'originalnetcost', 'netproceeds', 'gains']:
            stock[i] = str(
                round(float(stock[i].replace(',', '')), 2))
        stock['id'] = stock['salesdate'] +str(stock['netproceeds']
                                              .replace('.', '').replace(',', ''))
        return stock

    @staticmethod
    def format_stock_values(stock: dict) -> dict:
        # formats the data from the holdings page
        stock['currentvalue'] = str(
            round(float(stock['currentvalue'].replace(',', '')), 2))
        stock['netcost'] = str(
            round(float(stock['netcost'].replace(',', '')), 2))
        stock['currentprice_pershare'] = str(
            round(float(stock['currentprice_pershare'].replace(',', '')), 2))
        stock['netcost_pershare'] = str(
            round(float(stock['netcost_pershare'].replace(',', '')), 2))
        stock['id'] = str(stock['cusipid']) + str(
            stock['netcost'].replace('.', '').replace(',', ''))
        return stock

    @staticmethod
    def format_summary_values(data: dict) -> dict:
        # formats data from the summary page
        record = data['dataresult']['record']
        cash = float(record['cash_balance'].replace(',', '').replace('$', ''))
        shorts = - float(record['value_shorts'].replace(',', '').replace('$', ''))
        data['dataresult']['record']['cash_balance'] = '${:,}'.format(cash - shorts)
        data['dataresult']['record']['value_shorts'] = '${:,}'.format(shorts)
        return data
