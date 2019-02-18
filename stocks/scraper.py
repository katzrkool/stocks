import requests
from time import time
from datetime import datetime, timedelta
import xmltodict
from os import path
from json import dump
from stocks.analysis import Analyzer


class Scraper:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.s = requests.session()

    def go(self):
        self.login(self.username, self.password)

        summary = self.getSummary()
        summary = self.fixSummaryValues(summary)
        holdings = self.getHoldings()

        data = {**holdings, **summary}

        data['gainslosses'] = self.getRealizedGains()
        data['analytics'] = self.analytics(data)
        data['recent'] = self.getTransactions()

        self.save(data)

    def login(self, username: str, password: str):
        self.s.get('https://www.stockmarketgame.org/login.html')

        query = {'tpl': 'xmltpl/pingxml', '_': self.unixStamp()}
        self.s.get('https://www.stockmarketgame.org/cgi-bin/haipage/page.html', params=query)

        data = {'ACCOUNTNO': username,
                'USER_PIN': password,
                'SECURITY_STRING': ''}
        self.s.post('https://www.stockmarketgame.org/cgi-bin/hailogin', data=data)

    def unixStamp(self)-> str:
        return str(round(time()))

    def getTransactions(self) -> list:
        data = self.fetchXml('Administration/game/a_trad/cont_transnotes')
        return data['transactions']['record'][:4]

    def fetchXml(self, url: str) -> dict:
        query = {'tpl': url,
                 '_': self.unixStamp()}
        data = self.s.get(
            'https://www.stockmarketgame.org/cgi-bin/haipage/page.html',
            params=query).text
        data = '<xml id="xmlDataIsland">' + \
               data.split('<xml id="xmlDataIsland">')[1]
        data = data.split('</xml>')[0] + '</xml>'

        return dict(xmltodict.parse(data)['xml']['response'])

    def getSummary(self) -> dict:
        today = datetime.today()
        query = {'tpl': 'Administration/game/a_trad/pa_xml',
                 'fromdate': (today - timedelta(days=2)).strftime('%-m/%-d/%Y'),
                 'todate': today.strftime('%-m/%-d/%Y'),
                 'ticks': 'DAILY',
                 '_': self.unixStamp()}

        # this returns some xml, but I'm converting it to a dict because xml is no fun
        data = self.s.get('https://www.stockmarketgame.org/cgi-bin/haipage', params=query).text

        # also, they return non-valid xml so we must fix it
        data = data.replace('</html>', '</HTML>')
        data = dict(xmltodict.parse(data)['HTML']['xml']['response'])
        if int(data['dataresult']['noofrecords']) > 1:
            data['dataresult']['record'] = data['dataresult']['record'][-1]

        return data

    def getHoldings(self) -> dict:
        data = self.fetchXml('Administration/game/a_trad/cont_acctholdings')
        data['transactions']['record'] = [self.fixStockValues(i) for i in data['transactions']['record']]

        return data

    def getRealizedGains(self) -> list:
        data = self.fetchXml('Administration/game/a_trad/cont_gainsloss')

        data.pop('account_info')
        data = data['transactions']['record']

        return [self.fixRealizedValues(i) for i in data]

    # this stuff isn't fetching

    def fixRealizedValues(self, stock: dict) -> dict:
        for i in ['netcostpershare', 'netsalepershare', 'originalnetcost', 'netproceeds', 'gains']:
            stock[i] = str(
                round(float(stock[i].replace(',', '')), 2))
        stock['id'] = stock['salesdate'] + str(stock['netproceeds'].replace('.', '').replace(',', ''))
        return stock

    def fixStockValues(self, stock: dict) -> dict:
        stock['currentprice_pershare'] = str(
            round(float(stock['currentprice_pershare'].replace(',', '')), 2))
        stock['netcost_pershare'] = str(
            round(float(stock['netcost_pershare'].replace(',', '')), 2))
        stock['id'] = str(stock['cusipid']) + str(
            stock['netcost'].replace('.', '').replace(',', ''))
        return stock

    def fixSummaryValues(self, data: dict) -> dict:
        record = data['dataresult']['record']
        cash = float(record['cash_balance'].replace(',', '').replace('$', ''))
        shorts = - float(record['value_shorts'].replace(',', '').replace('$', ''))
        data['dataresult']['record']['cash_balance'] = '${:,}'.format(cash - shorts)
        data['dataresult']['record']['value_shorts'] = '${:,}'.format(shorts)
        return data

    def save(self, data: dict):
        currentDir = path.dirname(path.realpath(__file__))
        with open(path.join(currentDir, '../', 'data.json'), 'w') as f:
            dump(data, f)

    def analytics(self, data: dict) -> dict:
        a = Analyzer(data)
        return a.go()


if __name__ == '__main__':
    s = Scraper('***REMOVED***', '***REMOVED***')
    s.go()
