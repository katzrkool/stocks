class Analyzer:
    def __init__(self, SEC_FEE_PER_DOLLAR: float):
        self.SEC_FEE_PER_DOLLAR = SEC_FEE_PER_DOLLAR

    def analyze(self, data: dict) -> dict:
        analytics = {}
        analytics = {**analytics, **self.performance(data)}
        analytics['profitable_sell_prices'] = self.profitable_sell_price(data)

        return analytics

    def performance(self, data: dict):
        # Calculates the stock that is doing the best/worst
        top = {}
        worst = {}
        if 'transactions' in data:
            for i in data['transactions']['record']:
                if not top or float(i['per_unrealized_gainslosses']) > \
                            float(top['per_unrealized_gainslosses']):
                    top = i

                if not worst or float(i['per_unrealized_gainslosses']) < \
                                float(worst['per_unrealized_gainslosses']):
                    worst = i

        return {'topPerformer': top, 'worstPerformer': worst}

    def profitable_sell_price(self, data: dict) -> dict:
        '''
        For all stocks in record, calculates the point at which it's profitable to sell them

        returns: dict of profitable sell price where the stock/record id is the key,
            and the price (as a float) is the value
        '''
        if 'transactions' in data:
            profitable_sell_prices = {}
            for i in data['transactions']['record']:
                netcost = float(i['netcost'])
                stock_id = i['id']
                # Multiply the base net cost by the SEC fee, add $10, and divide by amount of shares
                profitable_sell_prices[stock_id] = round(((self.SEC_FEE_PER_DOLLAR * netcost) + \
                                                (netcost + 10) + 0.01) / float(i['shares_value']), 2)
                
            return profitable_sell_prices
            
        return {}

    def calculate_fees(self, stock_value: float) -> float:
        '''
        Inputs a stock's current value, and returns the net fees if sold at that value
        
        Fee price includes the buy price too
        '''
        return round((self.SEC_FEE_PER_DOLLAR *stock_value) + 10.01, 2)

class AuthError(Exception):
    # Incorrect username and password error

    def __init__(self):
        super().__init__('Incorrect username or password!')
        
class AlphaVantageError(Exception):
    pass