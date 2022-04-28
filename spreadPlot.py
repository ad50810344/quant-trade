from json.tool import main
from tqsdk import TqApi, TqAuth, TqAccount, tafunc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from time import *
from datetime import date

def spreadPlot():
    symbol1 = "SHFE.ag2207"
    symbol2 = "SHFE.ag2206"
    simnowAccout = TqAccount(broker_id= "simnow", account_id= "138411", password= "15221shuai")
    api = TqApi(account= simnowAccout, auth= TqAuth( "15221624883", "15221shuai"))

    #行情
    quote1_Tick = api.get_tick_serial(symbol1, 8000)
    quote2_Tick = api.get_tick_serial(symbol2, 8000)
    #时间格式转化
    quote1_Tick.datetime = quote1_Tick.datetime.map(tafunc.time_to_datetime)
    quote2_Tick.datetime = quote2_Tick.datetime.map(tafunc.time_to_datetime)
    #spread_tick序列
    spread_Ask_Tick = np.array(list(quote1_Tick.ask_price1)) - np.array(list(quote2_Tick.ask_price1))
    spread_Bid_Tick = np.array(list(quote1_Tick.bid_price1)) - np.array(list(quote2_Tick.bid_price1))
    #取样筛选spread
    spread_Ask_Tick = spread_Ask_Tick[0:-1:20]
    spread_Bid_Tick = spread_Bid_Tick[0:-1:20]
    #计算均值
    aver_spread_Ask = np.mean(spread_Ask_Tick)
    aver_spread_Bid = np.mean(spread_Bid_Tick)

    # x = np.arange(len(spread_Ask_Tick))
    # plt.plot(x, spread_Ask_Tick)
    # plt.show()

    position1= api.get_position(symbol1)
    position2= api.get_position(symbol2)

    #统计交易
    newOrders1 = {}
    orders1 = api.get_order()
    for k, v in orders1.items():
        if v["instrument_id"] == "ag2207":
            v["insert_date_time"] = tafunc.time_to_datetime(v["insert_date_time"])
            k = v["insert_date_time"]
            print(v)
                

    trades1 = api.get_trade()
    for k, v in trades1.items():
        if v["instrument_id"] == "ag2207":
            v["trade_date_time"] = tafunc.time_to_datetime(v["trade_date_time"])
            k = v["trade_date_time"]
            print(v)

    cld = api.get_trading_calendar(start_dt= date(2021,1,1), end_dt= date(2022,12,31))
    while api.wait_update():
        print(len(orders1), len(trades1))
    return


def plot():    
    return 

def main():
    spreadPlot()
    plot()

if __name__ == '__main__':
    main()
