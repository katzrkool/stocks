class Analyzer:
    def __init__(self, data: dict):
        self.data = data

    def analyze(self) -> dict:
        analytics = {}
        analytics = {**analytics, **self.performance()}

        return analytics

    def performance(self):
        # Calculates the stock that is doing the best/worst
        top = {}
        worst = {}
        if 'transactions' in self.data:
            for i in self.data['transactions']['record']:
                if not top or float(i['per_unrealized_gainslosses']) > \
                            float(top['per_unrealized_gainslosses']):
                    top = i

                if not worst or float(i['per_unrealized_gainslosses']) < \
                                float(worst['per_unrealized_gainslosses']):
                    worst = i

        return {'topPerformer': top, 'worstPerformer': worst}


class AuthError(Exception):
    # Incorrect username and password error

    def __init__(self):
        super().__init__('Incorrect username or password!')
        