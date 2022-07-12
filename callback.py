import sys
sys.path.append("/home/inie0722/company/strategysystem/build/lib")
sys.path.append('/home/QiuWenhao/cta_strategy')
from PyStrategySystem import *
import pandas as pd
import numpy as np
import datetime
import re
import os
import json
import joblib
from collections import defaultdict
import math
import time


class callbacks(object):
    def __init__(self, exchange_list, signal_list, multiplier, subscribe_bar, mykline, mykline_path, output_path, kline_limit, model_path, model_edition, exchange_config, printfile):

    def update(self, ticker, ticker_type, pos):
        #if type == quote_type.KLine + 300:
            #print( "is 300s bar", ticker.to_string(), type, pos, to_string(self.bar[300].get_bar(pos).time))
            #print(to_string(self.bar[300].get_bar(pos).time))
            #print(self.bar[300].get_bar(pos))

        contract_name = self.tickerToStr[int(ticker)]
        future = re.findall(r'([a-zA-Z]+)\d+\.', contract_name)[0]
        time_now = self.bar[contract_name].get_bar(pos).time + datetime.datetime(1970,1,1,8,0,0)
        #print('update', time_now)
        if pos >0:
            time_pre = self.bar[contract_name].get_bar(pos-1).time + datetime.datetime(1970,1,1,8,0,0)
        else:
            time_pre = time_now
        self.bar_pos[contract_name] = pos


        # 更新mykline
        for key, values in self.update_time.items():
            # 只有过了某个时间点才更新bar
            if key not in self.mykline:
                continue

            #print(time_now.time(), values[self.time_pointer[key][contract_name]], time_now.time() < values[self.time_pointer[key][contract_name]])
            # 已经触发2.30后触发的2.35bar不管
            if self.time_pointer[key][contract_name] >= len(values):
                continue

            if key in self.mykline and time_now.time() < values[self.time_pointer[key][contract_name]] \
                    and time_now.date() - time_pre.date() < pd.Timedelta(days=1):
                pre_pos = self.pre_bar_pos[key][contract_name]
                # 整体相后退一步，去掉最早的数据，给最新的数据留位置
                self.mykline_bar[key][contract_name] = self.mykline_bar[key][contract_name].shift(-1)

                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'LastPrice_open'] = self.bar[contract_name].get_bar(pre_pos).open_price
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'LastPrice_high'] = max(self.bar[contract_name].get_bar(i).high_price for i in range(pre_pos, pos + 1))
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'LastPrice_low'] = min(self.bar[contract_name].get_bar(i).low_price for i in range(pre_pos, pos + 1))
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'LastPrice_close'] = self.bar[contract_name].get_bar(pos).close_price

                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'Avg_price'] = sum(self.bar[contract_name].get_bar(i).avg_price for i in range(pre_pos, pos + 1))/(pos - pre_pos + 1)
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'Volume'] = sum(self.bar[contract_name].get_bar(i).volume for i in range(pre_pos, pos + 1))
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'Turnover'] =  sum(self.bar[contract_name].get_bar(i).amount for i in range(pre_pos, pos + 1))
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'OpenInterest_last'] = self.bar[contract_name].get_bar(pos).open_interest

                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'BidPrice1'] = self.bar[contract_name].get_bar(pos).bid_price1
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'AskPrice1'] = self.bar[contract_name].get_bar(pos).ask_price1
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'AveragePrice'] = self.bar[contract_name].get_bar(pos).average_price
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'UpperLimitPrice'] = self.bar[contract_name].get_bar(pos).upper_limit_price
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'LowerLimitPrice'] = self.bar[contract_name].get_bar(pos).lower_limit_price
                self.mykline_bar[key][contract_name].loc[self.kline_limit-1, 'Date'] = time_now

                open_price = self.bar[contract_name].get_bar(pre_pos).open_price
                my_signal = self.model[key][future].predict(self.mykline_bar[key][contract_name])[-1]
                self.my_signal[key][future].append([time_now, my_signal, open_price])
                self.pre_bar_pos[key][contract_name] = pos + 1
                self.exchange_order[key][contract_name] = [my_signal, True]

        return 0
    
    def order(self, ticker, ticker_type, pos):
        contract_name = self.tickerToStr[int(ticker)]
        time_now = self.ticker_bar[contract_name].get_quote(pos).time + datetime.datetime(1970,1,1,8,0,0)


        return 0

    def risk(self, ticker, ticker_type, pos):

        return 0
    

    def start(self, argc, argv):
        print("start")
        print(argc, argv)

        # 注册回调函数
        Signal_manager = SignalManager()
        ticker_manager = SignalManager()
        Signal_manager.add_signal("test_exchange", self.update)
        ticker_manager.add_signal("test_exchange2", self.risk)
        ticker_manager.add_signal("test_exchange", self.order)

        self.trader = TraderApi("./trader.json")

        # 订阅k线行情
        quote = env.drive().use_QuoteEvent()
        quote.load_config("./config.json")
        for item in self.exchange_list:
            future = re.findall(r'([a-zA-Z]+)\d+\.', item)[0]
            future_multiplier = self.multiplier[self.multiplier['future'] == future]['multiplier'].values[0]
            
            ticker = TickerID(item)
            self.tickerToStr[int(ticker)] = item

            quote.add_kline(ticker, self.subscribe_bar, 64, Signal_manager, future_multiplier)
            quote.sub_snapshot(ticker, ticker_manager)

            self.bar[item] = quote.get_kline(ticker, self.subscribe_bar)
            self.ticker_bar[item] = quote.get_quote_buffer(ticker)
            self.up_down_limit[item] = [quote.get_pStaticQuote(ticker).upper_limit_price, quote.get_pStaticQuote(ticker).lower_limit_price]
            

        for item in self.signal_list:
            future = re.findall(r'([a-zA-Z]+)\d+\.', item)[0]
            future_multiplier = self.multiplier[self.multiplier['future'] == future]['multiplier'].values[0]

            ticker = TickerID(item)
            self.tickerToStr[int(ticker)] = item

            quote.add_kline(ticker, self.subscribe_bar, 64, Signal_manager, future_multiplier)
            self.bar[item] = quote.get_kline(ticker, self.subscribe_bar)

        return 0

    def exit(self, code):
        print('99999')
        for key in self.mykline:
            for item in self.exchange_list + self.signal_list:
                future = re.findall(r'([a-zA-Z]+)\d+\.', item)[0]
                pre_pos = self.pre_bar_pos[key][item]
                pos = self.bar_pos[item]
                time_now = self.bar[item].get_bar(pos).time + datetime.datetime(1970, 1, 1, 8, 0, 0)
                # 这种情况需要我自己收一个bar
                if (self.time_pointer[key][item] < len(self.update_time[key]) and env.is_night() and self.update_time[key][self.time_pointer[key][item]] <= self.close_time_night[future])\
                        or (self.time_pointer[key][item] < len(self.update_time[key]) and not env.is_night() and self.update_time[key][self.time_pointer[key][item]] <= self.close_time_day):
                    self.mykline_bar[key][item] = self.mykline_bar[key][item].shift(-1)
                    print(time_now, self.bar[item].get_bar(pre_pos).open_price)
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'LastPrice_open'] = self.bar[item].get_bar(pre_pos).open_price
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'LastPrice_high'] = max(self.bar[item].get_bar(i).high_price for i in range(pre_pos, pos + 1))
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'LastPrice_low'] = min(self.bar[item].get_bar(i).low_price for i in range(pre_pos, pos + 1))
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'LastPrice_close'] = self.bar[item].get_bar(pos).close_price

                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'Avg_price'] = sum(self.bar[item].get_bar(i).avg_price for i in range(pre_pos, pos + 1)) / (pos - pre_pos + 1)
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'Volume'] = sum(self.bar[item].get_bar(i).volume for i in range(pre_pos, pos + 1))
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'Turnover'] = sum(self.bar[item].get_bar(i).amount for i in range(pre_pos, pos + 1))
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'OpenInterest_last'] = self.bar[item].get_bar(pos).open_interest

                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'BidPrice1'] = self.bar[item].get_bar(pos).bid_price1
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'AskPrice1'] = self.bar[item].get_bar(pos).ask_price1
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'AveragePrice'] = self.bar[item].get_bar(pos).average_price
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'UpperLimitPrice'] = self.bar[item].get_bar(pos).upper_limit_price
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'LowerLimitPrice'] = self.bar[item].get_bar(pos).lower_limit_price
                    self.mykline_bar[key][item].loc[self.kline_limit-1, 'Date'] = time_now
                    
                    open_price = self.bar[item].get_bar(pre_pos).open_price
                    my_signal = self.model[key][future].predict(self.mykline_bar[key][item])[-1]
                    self.my_signal[key][future].append([time_now, my_signal, open_price])

        for time_range, values in self.mykline_bar.items():
            for item, data in values.items():
                future = re.findall(r'([a-zA-Z]+)\d+\.', item)[0]
                contract_name = re.findall(r'(\w+)\.', item)[0]
                data.to_pickle(self.mykline_path + '/' + time_range + '/' + future + '/' + contract_name + '.pkl')
            for item in self.contract_list:
                res = pd.DataFrame(self.my_signal[time_range][item], columns=['Date', 'signal', 'open_price'])
                out_path = self.output_path +'/' + time_range + '/' + item + '.pkl'
                isExists = os.path.exists(out_path)
                if not isExists:
                    res.to_pickle(out_path)
                else:
                    pre_res = pd.read_pickle(out_path)
                    res = pd.concat([pre_res,res])
                    res.reset_index(drop=True, inplace=True)
                    res.to_pickle(out_path)


        print('本地时间:', time.strftime('%Y%m%d%H%M%S', time.localtime()))
        print("exit", code)
        return 0



def start(argc, argv):
    print("start")
    print(argc, argv)

    today = pd.to_datetime((env.date()+datetime.datetime(1970,1,1,8,0,0)).date())


    # 交易的合约list
    exchange_list = Exchange_index.loc[today, 'index']
    signal_list = []
    global xxx

    xxx = callbacks(exchange_list=exchange_list, signal_list=signal_list, multiplier=multiplier, subscribe_bar=subscribe_bar,
                    mykline=mykline, mykline_path=mykline_path, output_path=output_path, kline_limit=kline_limit,
                    model_path=model_path, model_edition=model_edition_data, exchange_config=exchange_config, printfile=printfile)
    xxx.start(argc, argv)

    print("env.drive")
    return 0

def exit(code):
    xxx.exit(code)
    print("exit", code)
    return 0
