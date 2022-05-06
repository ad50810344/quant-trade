import csv
from re import X
from tqsdk import TqApi, TqAuth, TqAccount, tafunc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from time import *
import datetime
from datetime import date

#列出市场价，报单价格，成交价格--->找出滑点证据
class analyse:
    def __init__(self, api, legA, legB):
        self.api = api
        self.legA = legA
        self.legB = legB
        pass

    def spreadPlot(self):
        symbol1 = "SHFE.ag2207"
        symbol2 = "SHFE.ag2206"
        
        #行情
        quote1_Tick = self.api.get_tick_serial(symbol1, 8000)
        quote2_Tick = self.api.get_tick_serial(symbol2, 8000)
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

        x = np.arange(len(spread_Ask_Tick))
        plt.plot(x, spread_Ask_Tick)
        plt.show()

        position1= self.api.get_position(symbol1)
        position2= self.api.get_position(symbol2)
        self.api.close()

    def getOrdersTrades(self):
        #统计交易
        header1 = ["instrument", "direction", "offset", "tradePrice", 
                    "volume",  "commission", "trade_time"]
        with open("trades.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames= header1)
            writer.writeheader()
            trades1 = self.api.get_trade()
            for k, v in trades1.items():
                if v["instrument_id"] == self.legA or v["instrument_id"] == self.legB :
                    v["trade_date_time"] = tafunc.time_to_str(v["trade_date_time"])
                    # k = v["trade_date_time"]
                    newTrades = {
                        'instrument': v["instrument_id"],
                        'direction': v["direction"],
                        'offset': v["offset"],
                        'tradePrice': v["price"],
                        'volume': v["volume"],
                        'commission': v["commission"],
                        'trade_time' : v["trade_date_time"],
                        # "askPrice": quote1_Tick.loc[v["trade_date_time"],quote1_Tick["ask_price1"]]
                        # "bidPrice":
                        # "sendPrice": 
                    }
                    writer.writerow(newTrades)
                # else: 
                #     print("no items")
        header2 = ["instrument", "direction", "offset", "insertPrice", "tradePrice",
                     "volumeOrigin", "volumeLeft", "insert_time", "lastMessage"]
        with open("orders.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames= header2)
            writer.writeheader()
            orders1 = self.api.get_order()
            for key, value in orders1.items():
                # writer.writerow([k, v])
                if value["instrument_id"] == self.legA or value["instrument_id"] == self.legB:
                    value["insert_date_time"] = tafunc.time_to_str(value["insert_date_time"])
                    key = value["insert_date_time"]
                    newInserts = {
                        "instrument": value["instrument_id"],
                        "direction": value["direction"],
                        "offset": value["offset"],
                        "insertPrice": value["limit_price"],
                        "tradePrice": value["trade_price"],
                        "volumeOrigin": value["volume_orign"],
                        "volumeLeft": value["volume_left"],
                        "insert_time" : value["insert_date_time"],
                        "lastMessage":value["last_msg"],
                        # "askPrice": quote1_Tick.loc[v["trade_date_time"],quote1_Tick["ask_Price1"]]
                        # "bidPrice":
                        # "tradePrice": 
                    }
                    writer.writerow(newInserts)
            #     else:
            #         print("no orders1")

        cld = self.api.get_trading_calendar(start_dt= date(2021,1,1), end_dt= date(2022,12,31))
        # while api.wait_update():
        #     # print(len(orders1), len(trades1))
        #     sleep(2)
        self.api.close()
        # return

    def handleOrdersTrades(self):    
        dfTrades = pd.read_csv("trades.csv")
        dfSort = dfTrades.sort_values("trade_time", ignore_index=True)
        dfSort.to_csv("trades.csv")

        dfOrders = pd.read_csv("orders.csv")
        dfSortOrders = dfOrders.sort_values("insert_time", ignore_index= True)
        dfSortOrders.to_csv("orders.csv")
        pass
    
def ui(api):
    klines1 = api.get_tick_serial("SHFE.ag2207", data_length = 1800)
    klines2 = api.get_tick_serial("SHFE.ag2206", data_length = 1800)

    plt.ion()
    # Create a figure and a set of subplots.
    figure, ax = plt.subplots()
    # return AxesImage object for using.
    lines, = ax.plot([], [])
    ax.set_autoscaley_on(True)
    # ax.set_xlim(min_x, max_x)
    ax.grid()
    while True:
        api.wait_update() 
        spread = np.array(list(klines1.ask_price1)) - np.array(list(klines2.ask_price1))
        xdata = np.arange(1800)
        ydata = spread.tolist()
        # print(ydata)
        # print(len(ydata))
        # print(klines1["close"].tolist())
        # print(len(klines1["close"].tolist()))
        # update x, y data
        lines.set_xdata(xdata)
        lines.set_ydata(ydata)
        #Need both of these in order to rescale
        ax.relim()
        ax.autoscale_view()
        # draw and flush the figure .
        figure.canvas.draw()
        figure.canvas.flush_events()

        # print(klines1["open"])
        sleep(1)

def main():
    simnowAccout = TqAccount(broker_id= "simnow", account_id= "138411", password= "15221shuai")
    api = TqApi(account= simnowAccout, auth= TqAuth( "15221624883", "15221shuai"))
    legA = "ag2207"
    legB = "ag2206"

    analy = analyse(api=api, legA=legA, legB=legB)
    # analy.spreadPlot()
    analy.getOrdersTrades()
    analy.handleOrdersTrades()
    # plotAnalyse()

if __name__ == '__main__':
    main()
