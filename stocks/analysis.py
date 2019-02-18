class Analyzer:
    def __init__(self, data: dict):
        self.data = data

    def go(self) -> dict:
        analytics = {}
        analytics = {**analytics, **self.performance()}

        return analytics

    def performance(self):
        top = None
        worst = None
        for i in self.data['transactions']['record']:
            if not top or float(i['per_unrealized_gainslosses']) > float(top['per_unrealized_gainslosses']):
                top = i

            if not worst or float(i['per_unrealized_gainslosses']) < float(worst['per_unrealized_gainslosses']):
                worst = i

        return {'topPerformer': top, 'worstPerformer': worst}
