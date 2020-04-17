import pandas as pd
import numpy as np
from findatapy.market import Market, MarketDataRequest, MarketDataGenerator
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from sklearn import linear_model
import itertools as it
from decimal import *
from chartpy import Chart, Style, Canvas
import time

getcontext().prec = 5
getcontext().rounding = ROUND_HALF_UP
market = Market(market_data_generator=MarketDataGenerator())

start = time.time()
folder = "c:\\users\\mibat\\downloads"
files = []
quali, stockrelatives, epr, eprvar, eprsd, eprsdaux, sml, orderedsml = {}, {}, {}, {}, {}, {}, {}, {}
sortedepr = []

market = Market(market_data_generator=MarketDataGenerator())

tempequitynames = input("Separados por comas, ingrese nombres para los activos a analizar: ")
tempequitytickers = input("Separados por comas, ingrese los tickers de dichos activos: ")
decimprec = int(input("Cuántos decimales? "))
startinput = input("Desde cuándo? (DD/MM/YYYY) ")
freq = input("Frecuencia de valores? ")

precision = list(range(0, 101, decimprec))

monthlist = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
datesoperand = startinput.split("/")
day = datesoperand[0] + ' '
month = monthlist[int(datesoperand[1])-1] + ' '
year = datesoperand[2]
start_date = datesoperand[0] + ' ' + monthlist[int(datesoperand[1])-1] + ' ' + datesoperand[2]

equitynames=tempequitynames.split(",")
equitytickers=tempequitytickers.split(",")

md_requestclose = MarketDataRequest(
            start_date=start_date,  # start date
            data_source='yahoo',  # use Bloomberg as data source
            tickers=equitynames,  # ticker (findatapy)
            fields=['close'],  # which fields to download
            vendor_tickers=equitytickers,  # ticker (Yahoo)
            vendor_fields=['Close'])
gendfclose = market.fetch_market(md_requestclose)
#print(gendfclose[gendfclose.columns[0]].tolist())

def purgedselect(subject,index):
    if not np.isnan(subject[index]) and subject[index] is not None:
        return subject[index]
    else:
        purgedselect(subject,(index-1))

class equity:
    def __init__(self, name, ticker):
        self.name = name
        self.ticker = ticker
        self.close = []
        self.rates = []
    def calc_values(self):
        for item in range(len(gendfclose[gendfclose.columns[equitynames.index(self.name)]].tolist())):
            self.close.append(purgedselect(gendfclose[gendfclose.columns[equitynames.index(self.name)]].tolist(),item))
        for item in range(len(self.close)):
            if self.close[item] != None:
                pass
            else:
                self.close[item] = self.close[item-1]
        #print(self.name)
        #print(self.close)
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
        #print(self.rates)

for number in range(len(equitynames)):
    asset = equity(equitynames[number],equitytickers[number])
    asset.calc_values()
    asset.addrates()
    asset_mean = np.mean(asset.rates)
    asset_std = np.std(asset.rates)
    quali.update({asset.name: [round(asset_mean, 7), round(asset_std, 7)]})

print(quali)

def all_expec_returns():
    expecretlist = []
    for i in range(len(equitynames)):
        asset = equity(equitynames[i],equitytickers[i])
        asset.calc_values()
        asset.addrates()
        expecretlist.append(np.mean(asset.rates))
    return expecretlist


#for i in files:
#   quali.update(stock_analysis(i))


def correl(stock1, stock2):
    asset1 = equity(equitynames[equitynames.index(stock1)],equitytickers[equitynames.index(stock1)])
    asset1.calc_values()
    asset1.addrates()
    asset2 = equity(equitynames[equitynames.index(stock2)],equitytickers[equitynames.index(stock2)])
    asset1.calc_values()
    asset1.addrates()
    rates1 = asset1.rates
    rates2 = asset2.rates
    return pearsonr(rates1, rates2)


def cov():
    absratelist = []
    for i in range(len(equitynames)):
        asset = equity(equitynames[i],equitytickers[i])
        asset.calc_values()
        asset.addrates()
        absratelist.append(asset.rates)
    #print(str(len(absratelist)) + " " + str(len(absratelist[0])) + " " + str(len(absratelist[1])))
    stack = np.vstack(absratelist)
    matrix = np.cov(stack)
    return matrix

def definitecorrel(equitynames):
    correlation = {}
    for i in equitynames:
        counter = 0
        for l in equitynames:
            if counter < len(equitynames):
                if counter == 0:
                    correlation[i] = [(correl(i, l))[0]]
                    counter += 1
                else:
                    correlation[i].append(correl(i, l)[0])
                    counter += 1
    for i in list(correlation):
        correlation[i[:-4]] = correlation[i]
        del correlation[i]
    return correlation


weights = [float(i) / 100 for i in precision]

for i in quali:
    stockrelatives[i] = []


def meanretsweights():
    for i in stockrelatives:
        for l in weights:
            if sum(stockrelatives[i]) != 1:
                stockrelatives[i].append(quali[i][0] * l)
            else:
                stockrelatives[i].append(0)


meanretsweights()


def portfolioreturns():
    rates = all_expec_returns()
    erp = it.product(weights, repeat=len(rates))
    for i in erp:
        aux = 0
        counter = 0
        if 0.96 < sum(i) < 1.04:
            for l in i:
                aux += Decimal(l * rates[counter])
                counter += 1
            epr[aux] = i


portfolioreturns()


def portfoliovariance():
    for portfolio in epr:
        eprvar[portfolio] = Decimal((np.dot(np.dot(epr[portfolio], cov()), np.transpose(epr[portfolio]))))


portfoliovariance()

#print(eprvar)

for i in eprvar:
    eprsdaux[i] = eprvar[i].sqrt()
#print(eprsdaux)
eprsd = {value: key for (key, value) in eprsdaux.items()}

#print(eprsd)

for i in epr:
    sml[eprsdaux[i], i] = epr[i]

sortedeprsd = sorted(eprsd.keys())

for i in sortedeprsd:
    sortedepr.append(eprsd[i])

actualdict = {}

def create_graph_dict():
    count = 0
    while count < len(sortedepr):
        couple = [sortedeprsd[count], sortedepr[count]]
        actualdict[sortedeprsd[count], sortedepr[count]] = sml[couple[0], couple[1]]
        count += 1
    actualdict.update()

create_graph_dict()

sortedepr = [float(i) for i in sortedepr]
sortedeprsd = [float(i) for i in sortedeprsd]

plt.scatter(sortedeprsd,sortedepr)
plt.show()
gendfclose.columns = [i for i in equitynames]

def get_all_rates():
    rateslist = []
    for i in range(len(equitynames)):
        element = equity(equitynames[i],equitytickers[i])
        element.calc_values()
        element.addrates()
        rateslist.append(element.rates)
    return rateslist

def concoct_variables(explanatory):
    length = range(len(explanatory[0]))
    data = [[] for i in length]
    counter = 0
    subcounter = 0
    for number in length:
        for element in explanatory[:-1]:
            data[counter].append(element[subcounter])
        subcounter += 1
        counter += 1
    return data

print(get_all_rates()[:-1])

maybe_regression = linear_model.LinearRegression()
maybe_regression.fit(concoct_variables(get_all_rates()),get_all_rates()[-1])

#LinearRegression(copy_X=True, fit_intercept=True, n_jobs=None,normalize=False)

print(maybe_regression.coef_)

graphdf = pd.DataFrame(data=sortedepr, index=sortedeprsd, columns=["Expected Returns"])

stockchart = Chart(df=graphdf, engine='bokeh', chart_type='scatter', style=Style(title="Testing Chartpy", source="Yahoo Finance/Findatapy"))

canvas = Canvas(stockchart)

canvas.generate_canvas(silent_display = False, canvas_plotter = "plain")

end = time.time()
print(end - start)
