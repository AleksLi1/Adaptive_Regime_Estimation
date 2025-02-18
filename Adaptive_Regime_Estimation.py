"""See pg.6 of https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3272080 for further explanation"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import pandas_market_calendars as mcal
from functions import start_of_year

# Main Variables (some are defined in the paper)
start = '2003-01-01'
end = '2021-08-01'
tickers = ['QQQ', 'SPY', 'TLT']
gamma = 1.5
starting_capital = 10000

# Gather and Process Ticker Data
prices = yf.download(tickers=tickers, start=start, end=end)['Close'].dropna(axis=0)
prices['SPY_Daily_Ret'] = np.log(prices['SPY']/prices['SPY'].shift(1))
prices['TLT_Daily_Ret'] = np.log(prices['TLT']/prices['TLT'].shift(1))

# Define trading dates
year_end = pd.date_range(start, end, freq='Y').strftime('%Y-%m-%d').tolist()
year_start = [start_of_year(x) for x in year_end]
date_range = list(zip(year_start, year_end))
trading_year_start = []
trading_year_end = []
nyse = mcal.get_calendar('NYSE')
for k, v in date_range:
    nyse_trading_date_range = nyse.schedule(k, v)
    nyse_trading_date_range_index = mcal.date_range(nyse_trading_date_range, frequency='1D') \
        .strftime('%Y-%m-%d') \
        .tolist()
    trading_year_start.append(nyse_trading_date_range_index[0])
    trading_year_end.append(nyse_trading_date_range_index[-1])
trading_date_range = list(zip(trading_year_start, trading_year_end))

# Make lists of trading returns
SPY_returns = [prices['SPY_Daily_Ret'].loc[k:v].sum() for k, v in trading_date_range]
TLT_returns = [prices['TLT_Daily_Ret'].loc[k:v].sum() for k, v in trading_date_range]
rho_returns = list(zip(SPY_returns, TLT_returns))

# Monthly Rho Calculation
rho_calculation = [(1 + k)/(1 + v) for k, v in rho_returns]
rho_yearly = list(zip(trading_year_start, rho_calculation))

# Signal
# Previous month's Rho and 1
rho_df = pd.DataFrame(rho_yearly).set_index(0)
rho_df.columns = ['rho']
nyse_trading_date_range = nyse.schedule(trading_year_start[0], trading_year_end[-1])
nyse_trading_date_range_index = mcal.date_range(nyse_trading_date_range, frequency='1D') \
    .strftime('%Y-%m-%d') \
    .tolist()
rho_df = rho_df.reindex(nyse_trading_date_range_index, method='ffill')
rho_df['condition1'] = np.where(rho_df['rho'] >= 1, 1, 0)

# Mean and Standard Deviation calculations
rho_df['mean'] = rho_df['rho'].expanding(2).mean()
rho_df['std'] = rho_df['rho'].expanding(2).std()

# Mean and Std against Rho
signal_condition2 = [(rho_df['rho'] - rho_df['mean']) < gamma*rho_df['std']]
rho_df['condition2'] = np.select(signal_condition2, [1])

# Standardise data across dataframes
rho_index_list = rho_df.index.tolist()
prices = prices.loc[rho_index_list[0]:rho_index_list[-1]]

# Trading Signal
final_condition = [(rho_df['condition1'] == 1) & (rho_df['condition2'] == 1)]
prices['signal'] = np.select(final_condition, ['True'])

# Create portfolio value column
prices['Tomorrows Returns'] = 0
prices['Tomorrows Returns'] = np.log(prices['QQQ']/prices['QQQ'].shift(1))
prices['Tomorrows Returns'] = prices['Tomorrows Returns'].shift(-1)
prices['Tomorrows Returns'] = np.where(prices['signal'] == str(0), 0, prices['Tomorrows Returns'])
prices['Tomorrows Returns'] += 1
prices['Portfolio Value'] = 0
prices.at[nyse_trading_date_range_index[0], 'Portfolio Value'] = starting_capital
prices = prices.reset_index(drop=False)
for i, row in prices.iterrows():
    if i == 0:
        prices.loc[i, 'Portfolio Value'] = prices['Portfolio Value'].iat[0]
    else:
        prices.loc[i, 'Portfolio Value'] = prices.loc[i, 'Tomorrows Returns'] * \
                                           prices.loc[i - 1, 'Portfolio Value']
prices = prices.set_index('Date')

# Create benchmark column
prices['Market Returns'] = 0
prices['Market Returns'] = np.log(prices['SPY']/prices['SPY'].shift(1))
prices['Market Returns'] = prices['Market Returns'].shift(-1)
prices['Market Returns'] += 1
prices['Benchmark Value'] = 0
prices.at[nyse_trading_date_range_index[0], 'Benchmark Value'] = starting_capital
prices = prices.reset_index(drop=False)
for i, row in prices.iterrows():
    if i == 0:
        prices.loc[i, 'Benchmark Value'] = prices['Benchmark Value'].iat[0]
    else:
        prices.loc[i, 'Benchmark Value'] = prices.loc[i, 'Market Returns'] * \
                                           prices.loc[i - 1, 'Benchmark Value']
prices = prices.set_index('Date')

prices['Portfolio Value'].plot(label='Portfolio Value')
prices['Benchmark Value'].plot(label='SPY')
plt.legend()
plt.show()

# Calculate portfolio statistics
# Calculate portfolio drawdown
rolling_max_portfolio = prices['Portfolio Value'].rolling(252, min_periods=1).max()
daily_drawdown_portfolio = prices['Portfolio Value']/rolling_max_portfolio - 1.0
max_daily_drawdown_portfolio = daily_drawdown_portfolio.rolling(252, min_periods=1).min()
daily_drawdown_portfolio.plot()
plt.xticks(rotation=45)
plt.title('Portfolio Max Drawdown')
plt.show()
print('------------------------------------------')
print('Max portfolio drawdown: {:.2%}'.format(round((daily_drawdown_portfolio.min()), 2)))

# Annual portfolio returns
prices['Tomorrows Returns'] -= 1
portfolio_annual_return = prices['Tomorrows Returns'].rolling(252).sum().mean()
print('Average annual portfolio return: {:.2%}'.format(portfolio_annual_return))

# Portfolio Sharpe
portfolio_sharpe = prices['Tomorrows Returns'].mean() / prices['Tomorrows Returns'].std()
portfolio_sharpe_annualised = (250**0.5) * portfolio_sharpe
print('Portfolio Sharpe ratio: {:.2}'.format(portfolio_sharpe_annualised))

# Calculate market drawdown
rolling_max_market = prices['Benchmark Value'].rolling(252, min_periods=1).max()
daily_drawdown_market = prices['Benchmark Value']/rolling_max_market - 1.0
max_daily_drawdown_market = daily_drawdown_market.rolling(252, min_periods=1).min()
print('------------------------------------------')
print('Max market drawdown: {:.2%}'.format(round((daily_drawdown_market.min()), 2)))

# Annual market returns
prices['Market Returns'] -= 1
market_annual_return = prices['Market Returns'].rolling(252).sum().mean()
print('Average market return: {:.2%}'.format(market_annual_return))

# Market Sharpe
market_sharpe = prices['Market Returns'].mean() / prices['Market Returns'].std()
market_sharpe_annualised = (250**0.5) * market_sharpe
print('Market Sharpe ratio: {:.2}'.format(market_sharpe_annualised))
print('------------------------------------------')
