import time
from findatapy.market import Market, MarketDataRequest, MarketDataGenerator

start = time.time()
quali={}
tempequitynames = input("Separados por comas, ingrese nombres para los activos a analizar: ")
tempequitytickers = input("Separados por comas, ingrese los tickers de dichos activos: ")

equitynames=tempequitynames.split(",")
equitytickers=tempequitytickers.split(",")

class equity:
    def __init__(self,name,ticker):
        self.name = name
        self.ticker = ticker
        self.close = []
        self.rates = []
    def calc_values(self):
        market=Market(market_data_generator=MarketDataGenerator())
        md_request = MarketDataRequest(
            start_date="decade",  # start date
            data_source='yahoo',  # use Bloomberg as data source
            tickers=self.name,  # ticker (findatapy)
            fields=['close'],  # which fields to download
            vendor_tickers=self.ticker,  # ticker (Yahoo)
            vendor_fields=['Close'])
        gendclose = market.fetch_market(md_request)
        self.close.append(gendclose[gendclose.columns[0]].tolist())
    def addrates(self):
        counter = 0
        lmao = []
        for i in self.close:
            if counter == 0:
                counter += 1
            else:
                returns = (i - self.close[counter - 1]) / self.close[counter - 1]
                lmao.append(round(returns, 7))
                counter += 1
        self.rates = lmao[:-2]

for number in range(len(equitynames)):
    asset = equity(equitynames[number],equitytickers[number])
    asset.calc_values()
    asset.addrates()
    asset_mean = np.mean(asset.rates)
    asset_std = np.std(asset.rates)
    quali.update({asset.name: [round(asset_mean, 7), round(asset_std, 7)]})

print(quali)
end = time.time()

print(end-start)