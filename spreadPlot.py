import csv
from json.tool import main
from tqsdk import TqApi, TqAuth, TqAccount, tafunc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from time import *
from datetime import date

#列出市场价，报单价格，成交价格--->找出滑点
def spreadPlot():
    symbol1 = "SHFE.ag2207"
    symbol2 = "SHFE.ag2206"
    simnowAccout = TqAccount(broker_id= "simnow", account_id= "", password= "")
    api = TqApi(account= simnowAccout, auth= TqAuth( "", ""))

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
    header1 = ["instrument", "direction", "offset", "tradePrice", "volume", "trade_time", "commission"]
    with open("trades.csv", "wb", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames= header1)
        writer.writeheader()
    trades1 = api.get_trade()
    for k, v in trades1.items():
        # writer.writerow([k, v])
        if v["instrument_id"] == "ag2207" and v["order_id"] == 'SERVER.990.f40a7a78.3':
            v["trade_date_time"] = tafunc.time_to_str(v["trade_date_time"])
            k = v["trade_date_time"]
            newTrades = {
                "instrument": v["instrument_id"],
                "direction": v["direction"],
                "offset": v["offset"],
                "trdePrice": v["price"],
                "volume": v["volume"],
                "commission": v["commission"],
                "trade_time" : v["trade_date_time"]
                # "askPrice": quote1_Tick.loc[v["trade_date_time"],quote1_Tick["ask_Price1"]]
                # "bidPrice":
                # "sendPrice": 

            }
            print(newTrades)
            writer.writerows(newTrades)
        else: 
            print("no items")

    header2 = ["instrument", "direction", "offset", "insertPrice", "volume", "insert_time"]
    with open("orders.csv", "wb", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames= header2)
        writer.writeheader()
    orders1 = api.get_trade()
    for key, value in orders1.items():
        # writer.writerow([k, v])
        if value["instrument_id"] == "ag2207" and value["order_id"] == 'SERVER.990.f40a7a78.3':
            value["insert_date_time"] = tafunc.time_to_str(value["insert_date_time"])
            key = value["insert_date_time"]
            newInserts = {
                "instrument": value["instrument_id"],
                "direction": value["direction"],
                "offset": value["offset"],
                "insertPrice": value["price"],
                "volume": value["volume"],
                "insert_time" : value["insert_date_time"]
                # "askPrice": quote1_Tick.loc[v["trade_date_time"],quote1_Tick["ask_Price1"]]
                # "bidPrice":
                # "tradePrice": 

            }
            print(newInserts)
            writer.writerows(newInserts)
            
    cld = api.get_trading_calendar(start_dt= date(2021,1,1), end_dt= date(2022,12,31))
    # while api.wait_update():
    #     print(len(orders1), len(trades1))
    #     sleep(2)
    api.close()
    return

def plotAnalyse():    
    file = pd.read_csv("trades.csv")
    df = pd.DataFrame(file)
    dfIndex = df.sort_index(level= "trade_date_time")

    return 

def main():
    symbolList = ["ag2207", "ag2206"]
    spreadPlot()
    plotAnalyse()

if __name__ == '__main__':
    main()
