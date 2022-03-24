import talib as ta
import binance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("seaborn")
from itertools import product
import datetime
import warnings
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

class MA_Cross_Backtester():
    ''' 
    Class for the vectorized backtesting of SMA-based trading strategies.
    '''

    def __init__(self, coin, timeframe, sma_s, sma_l, start,end, api_key, secret_key):
        '''
        Parameters
        ----------
        coin: str
            ticker of the coin to be backtested
        timeframe: str
            intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M || m -> minutes; h -> hours; d -> days; w -> weeks; M -> months
        SMA_S: int
            periods of the fast moving average
        SMA_L: int
            periods of the low moving average
        start: str timestamp
            start date for data download
        end: str datetime
            end date 


        '''
        
        self.coin = coin
        self.timeframe = timeframe
        self.SMA_S = sma_s
        self.SMA_L = sma_l
        self.start = start
        self.end = end
        self.api_key = api_key
        self.secret_key = secret_key
        self.results = None 
        self.get_data()
        self.prepare_data()
        
    def __repr__(self):
        return "Backtest SMA Cross(Coin = {}, SMA_S = {}, SMA_L = {}, start = {})".format(self.coin, self.SMA_S, self.SMA_L, self.start)
        
    def get_data(self):
        ''' 
        Download from binance with get_historical_klines_generator.
        '''
        date = []
        open = []
        high = []
        low = []
        close = []
        volume = []

        api = binance.Client(self.api_key, self.secret_key)

        try:

            for i in api.get_historical_klines_generator(self.coin, self.timeframe,start_str=self.start):

                date.append(pd.to_datetime(i[0], unit='ms'))
                open.append(float(i[1]))
                high.append(float(i[2]))
                low.append(float(i[3]))
                close.append(float(i[4]))
                volume.append(int(float(i[5])))

            df = pd.DataFrame({'date':date, 'open':open, 'high':high, 'low':low, 'close':close, 'volume':volume}).set_index('date')
            df['returns'] = np.log(df.close.div(df.close.shift(1)))
            df.dropna(inplace = True)
            self.data = df
            return df

        except Exception as e:
            return("Error: {}".format(e))

    def prepare_data(self):
        '''Prepares the data for strategy backtesting (strategy-specific).
        '''
        data = self.data.copy()
        data["SMA_S"] = data["close"].rolling(self.SMA_S).mean()
        data["SMA_L"] = data["close"].rolling(self.SMA_L).mean()
        self.data = data
        
    def set_parameters(self, SMA_S = None, SMA_L = None):
        ''' Updates SMA parameters and the prepared dataset.
        '''
        if SMA_S is not None:
            self.SMA_S = SMA_S
            self.data["SMA_S"] = self.data["close"].rolling(self.SMA_S).mean()
        if SMA_L is not None:
            self.SMA_L = SMA_L
            self.data["SMA_L"] = self.data["close"].rolling(self.SMA_L).mean()
            
    def test_strategy(self):
        ''' Backtests the SMA-based trading strategy.
        '''
        data = self.data.copy().dropna()
        data = data.loc[:self.end].copy()
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)
        data["strategy"] = data["position"].shift(1) * data["returns"]
        data.dropna(inplace=True)
        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        self.results = data
       
        perf = data["cstrategy"].iloc[-1] # absolute performance of the strategy
        outperf = perf - data["creturns"].iloc[-1] # out-/underperformance of strategy
        return round(perf, 6), round(outperf, 6)
    
    def plot_results(self):
        ''' Plots the performance of the trading strategy and compares to "buy and hold".
        '''
        if self.results is None:
            print("Run test_strategy() first.")
        else:
            title = "{} | SMA_S = {} | SMA_L = {}".format(self.coin, self.SMA_S, self.SMA_L)
            self.results[["creturns", "cstrategy"]].plot(title=title, figsize=(12, 8))
            plt.savefig("backtest_strategy")
            return plt.show()
    
    def optimize_parameters(self, SMA_S_range, SMA_L_range):
        
        combinations = list(product(range(*SMA_S_range), range(*SMA_L_range)))

        # test all combinations
        results = []

        for comb in combinations:
            self.set_parameters(comb[0], comb[1])
            results.append(self.test_strategy()[0])

        best_perf = np.max(results) # best performance
        opt = combinations[np.argmax(results)] # optimal parameters


        # run/set the optimal strategy
        self.set_parameters(opt[0], opt[1])
        self.test_strategy()
                   
        # create a df with many results
        many_results =  pd.DataFrame(data = combinations, columns = ["SMA_S", "SMA_L"])
        many_results["performance"] = results
        self.results_overview = many_results
                            
        return [opt, best_perf]

class MA_Cross_Signal():

    def __init__(self, symbol,timeframe ,fast_ma_period, low_ma_period):

        self.symbol = symbol
        self.timeframe = timeframe
        self.fast_ma_period = fast_ma_period
        self.low_ma_period = low_ma_period

    
    def get_signal(self, api_key, secret_key):

        try:

            api = binance.Client(api_key, secret_key)
            df = pd.DataFrame(api.get_klines(symbol =self.symbol, interval=self.timeframe, limit=200)).loc[:,0:6]
            df[0] = pd.to_datetime(df[0], unit='ms')
            df[6] = pd.to_datetime(df[6], unit='ms')
            df = df.loc[df[6] < datetime.datetime.utcnow()] #Function to filter only close candles

            close = df[4].apply(lambda x: float(x))

            fast_ma = ta.SMA(close, timeperiod=self.fast_ma_period)
            low_ma = ta.SMA(close, timeperiod=self.low_ma_period)

            #sprint(df.tail(1))
            #print(fast_ma.iloc[-1], fast_ma.iloc[-2])

            #if fast_ma.iloc[-1] > low_ma.iloc[-1] and fast_ma.iloc[-2] < low_ma.iloc[-2]:

            if fast_ma.iloc[-1] > low_ma.iloc[-1]:
                return("buy")

            #elif fast_ma.iloc[-1] < low_ma.iloc[-1] and fast_ma.iloc[-2] > low_ma.iloc[-2]:

            elif fast_ma.iloc[-1] < low_ma.iloc[-1]:
                return("sell")

            else:
                return("no signal")

        except Exception as e:
            print("Error: {}".format(e))

class Bollinger_Bands_Strategy:

    def __init__(self, symbol, timeframe, bb_period, std):
        self.symbol = symbol
        self.timeframe = timeframe
        self.bb_period = int(bb_period)
        self.std = std

    def get_data(self, start_date, end_date):

        #Get data
        try:

            df = pd.read_csv("./market_data_crypto/{}_{}.csv".format(self.symbol, self.timeframe))
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df['bpr'] = abs(df['close'] - df['open']) / (df['high'] - df['low'])
            #df['sma'] = ta.SMA(df['close'], timeperiod=7)
            df['returns'] = np.log(df.close.div(df.close.shift(1)))
            df = df.loc[start_date:end_date]

            df['position'] = np.where((df.close > df.close.shift(1)) & (df.close.shift(1) > df.close.shift(2)) & (df.bpr > 0.7),1,
                            np.where((df.close < df.close.shift(1)) & (df.close.shift(1) < df.close.shift(2)) & (df.bpr > 0.7),-1,0))


            # df['position'] = np.where((df.close > df.close.shift(1)) & (df.close.shift(1) > df.close.shift(2)) & (df.bpr > 0.7) & (df.sma > df.sma.shift(1)),1,
            #                 np.where((df.close < df.close.shift(1)) & (df.close.shift(1) < df.close.shift(2)) & (df.bpr > 0.7) & (df.sma < df.sma.shift(1)),-1,
            #                 np.where(df.returns > 0.2,0,0)))

            for i,j in enumerate(df['position']):
                if (j == 0) == True:
                    df['position'][i] = df['position'][i-1]

            df["strategy"] = df.position.shift(1) * df["returns"]

        except Exception as e:
            print("Error: {}".format(e))

        return df

    def backtest(self):
        
        """
        Plot the Equity 
        """
        df = self.get_data()

        df[["returns", "strategy"]].sum() # absolute performance
        df[["returns", "strategy"]].sum().apply(np.exp) # absolute performance
        df[["returns", "strategy"]].mean() * 252 # annualized return
        df[["returns", "strategy"]].std() * np.sqrt(252) # annualized risk
        df["creturns"] = df["returns"].cumsum().apply(np.exp)
        df["cstrategy"] = df["strategy"].cumsum().apply(np.exp)

        df[["creturns", "cstrategy"]].plot(figsize = (12, 8), title = "Strategy - Double Soldiers at {} - {}".format(self.symbol, self.timeframe), fontsize = 12)
        plt.legend(fontsize = 12)
        plt.savefig("backtest_strategy")
        return df

    def get_signal(self, api_key, secret_key):

        try:

            api = binance.Client(api_key, secret_key)
            df = pd.DataFrame(api.get_klines(symbol =self.symbol, interval=self.timeframe, limit=50)).loc[:,0:6]
            df[0] = pd.to_datetime(df[0], unit='ms')
            df[6] = pd.to_datetime(df[6], unit='ms')            
            df = df.loc[df[6] < datetime.datetime.utcnow()] #Function to filter only close candles
            df[1] = df[1].apply(lambda x: float(x))
            df[2] = df[2].apply(lambda x: float(x))
            df[3] = df[3].apply(lambda x: float(x))
            df[4] = df[4].apply(lambda x: float(x))
            
            upperbb, middlebb, lowerbb = ta.BBANDS(df[4], timeperiod = self.bb_period, nbdevup = self.std, )
            print([upperbb, middlebb, lowerbb])

            #print(df)

            width = (upperbb / lowerbb ) / middlebb 
            width.dropna(inplace=True)
            print(width)

            # dist = upperbb.iloc[-1] / lowerbb.iloc[-1] 
            # print(upperbb.iloc[-1],lowerbb.iloc[-1] ,dist)


            # if df[4].iloc[-1] > df[4].iloc[-2] and df[4].iloc[-2] > df[4].iloc[-3] and float(df['bpr'].iloc[-1]) > 0.7:
            #     return("buy")

            # #elif fast_ma.iloc[-1] < low_ma.iloc[-1] and fast_ma.iloc[-2] > low_ma.iloc[-2]:

            # if df[4].iloc[-1] < df[4].iloc[-2] and df[4].iloc[-2] < df[4].iloc[-3] and float(df['bpr'].iloc[-1]) > 0.7:
            #     return("sell")

            # else:
            #     return("no signal")


        except Exception as e:
            print("Error: {}".format(e))


