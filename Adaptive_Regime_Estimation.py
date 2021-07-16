"""See pg.6 of https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3272080 for further explanation"""
import pandas as pd
import numpy as np
import yfinance as yf

#Main Variables (defined in the paper)
tickers = ['VFINX', 'VUSTX']
Gamma = 1.5

#Gather and Process Ticker Data
prices = yf.download(tickers=tickers)['Adj Close']
prices = prices.dropna(axis=0)
daily_ret = np.log(prices / prices.shift(1))[1:]
monthly_ret = daily_ret.groupby(pd.Grouper(freq='M')).apply(np.sum)
annual_ret = daily_ret.groupby(pd.Grouper(freq='Y')).apply(np.sum)

#Rho Calculation
rho_annual = (1 + annual_ret['VFINX'])/(1 + annual_ret['VUSTX'])
rho_annual_std = rho_annual.std()
rho_annual_mean = rho_annual.mean()

#Para-Contra Momentum Return Message
if rho_annual[-1] < 1 or (rho_annual[-1]-rho_annual_mean) >= (Gamma * rho_annual_std):
    print("It's a Contra-Momentum Period!")

if rho_annual[-1] >= 1 and (rho_annual[-1]-rho_annual_mean) < (Gamma * rho_annual_std):
    print("It's a Para-Momentum Period!")