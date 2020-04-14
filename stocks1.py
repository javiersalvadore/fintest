import pandas as pd
import numpy as np
import matplotlib as plt
from scipy.stats import pearsonr
import itertools as it
import os

folder = "c:\\users\\mibat\\downloads"
files = []

for r,d,f in os.walk(folder):
    for i in f:
        if ".csv" in i and i[2].isupper() and "(" not in i:
            files.append(i)
            
def tidyup(files = files):
    amo = len(files)/2
    for i in files:
        counter = 0
        for l in files:
            if pd.read_csv(i)["Date"].tolist() == pd.read_csv(l)["Date"].tolist():
                counter+=1
        if counter < amo:
            files.remove(i)

tidyup()

filenames = [i[:-4] for i in files]

def rateslist(stock):
    close_values = pd.read_csv(stock)["Close"].tolist()[1:]
    counter = 0
    rates = []
    for i in close_values:
        if counter == 0:
            counter += 1
        else:
            returns = (i-close_values[counter-1])/close_values[counter-1]
            rates.append(returns)
            counter+=1
            rates.append(returns)
    rates = rates[:-2]
    return rates

def stock_analysis(stock):
    rates_mean = np.mean(rateslist(stock))
    rates_sd = np.std(rateslist(stock))
    stock_name = stock[:-4]
    return {stock_name:[rates_mean, rates_sd]}

def all_expec_returns(files):
    expecretlist = []
    for i in files:
        expecretlist.append(np.mean(rateslist(i)))
    return expecretlist

quali = {}
for i in files:
    quali.update(stock_analysis(i))

def correl(stock1,stock2):
    rates1 = rateslist(stock1)
    rates2 = rateslist(stock2)    
    return pearsonr(rates1,rates2)

def cov(files=files):
    absratelist=[]
    for i in files:
        absratelist.append(rateslist(i))
    stack = np.vstack(absratelist)
    matrix = np.cov(stack)
    return matrix

def definitecorrel(files):
    correlation = {}
    for i in files:
        counter = 0
        for l in files:
            if counter < len(files):
                if counter == 0:
                    correlation[i] = [(correl(i,l))[0]]
                    counter += 1
                else:
                    correlation[i].append(correl(i,l)[0])
                    counter += 1
    for i in list(correlation):
        correlation[i[:-4]] = correlation[i]
        del correlation[i]
    return correlation

weights = [i/100 for i in list(range(0,101, 10))]

stockrelatives = {}
for i in quali:
    stockrelatives[i] = []
def meanretsweights(files):
    for i in stockrelatives:
        for l in weights:
            stockrelatives[i].append(quali[i][0]*l)

meanretsweights(files)

epr = {}


def portfolioreturns():
    rates = all_expec_returns(files)
    erp = it.product((weights),repeat=len(rates))
    for i in erp:
        aux = 0
        counter = 0
        if 0.96 < sum(i) < 1.04:
            for l in i:
                aux += l*rates[counter]
                counter += 1
            epr[aux] = i
    
portfolioreturns()

eprvar = {}

def portfoliovariance():
    for portfolio in epr:
        eprvar[portfolio] = np.dot(np.dot(epr[portfolio], cov()),np.transpose(epr[portfolio]))

portfoliovariance()
print(eprvar)
print(end-start)