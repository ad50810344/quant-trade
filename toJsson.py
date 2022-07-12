from datetime import date
import numpy as np
import pandas as pd
import json
from simplejson import load
import statsmodels.tsa.stattools as st

#0315

dataFile1 = {"file1": "/home/DuShuai/CSV/out/cu2204.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/cu2205.SHFE-2022-0311.csv"}

dataFile2 = {"file1": "/home/DuShuai/CSV/out/al2204.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/al2205.SHFE-2022-0311.csv"}

dataFile3 = {"file1": "/home/DuShuai/CSV/out/zn2204.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/zn2205.SHFE-2022-0311.csv"}

dataFile4 = {"file1": "/home/DuShuai/CSV/out/pb2204.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/pb2205.SHFE-2022-0311.csv"}

dataFile5 = {"file1": "/home/DuShuai/CSV/out/sn2204.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/sn2205.SHFE-2022-0311.csv"}

dataFile6 = {"file1": "/home/DuShuai/CSV/out/ni2204.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/ni2205.SHFE-2022-0311.csv"}

dataFile7 = {"file1": "/home/DuShuai/CSV/out/au2208.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/au2206.SHFE-2022-0311.csv"}

dataFile8 = {"file1": "/home/DuShuai/CSV/out/ag2207.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/ag2206.SHFE-2022-0311.csv"}

dataFile9 = {"file1": "/home/DuShuai/CSV/out/ru2209.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/ru2205.SHFE-2022-0311.csv"}

dataFile10 = {"file1": "/home/DuShuai/CSV/out/sn2205.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/sn2204.SHFE-2022-0311.csv"}

dataFile11 = {"file1": "/home/DuShuai/CSV/out/ss2205.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/ss2204.SHFE-2022-0311.csv"}

dataFile12 = {"file1": "/home/DuShuai/CSV/out/rb2210.SHFE-2022-0311.csv", 
            "file2":"/home/DuShuai/CSV/out/rb2205.SHFE-2022-0311.csv"}

def tradeFee():
    data = pd.read_csv("arbitrage-trade/合约数据/data.csv")
    data1 = pd.read_csv("arbitrage-trade/合约数据/合约乘数.csv")
    data2 = pd.read_csv("arbitrage-trade/合约数据/交易参数.csv")
    data['费率开仓'] = data["交易手续费率(‰)"] * data["结算价"] / 100
    #[‘费额开仓’]
    data["平今"] = data['费率开仓'] * data['平今折扣率(%)'] / 100
    data["平今2"] = data['交易手续费额(元/手)'] * data['平今折扣率(%)'] / 100

    data['汇总开仓手续费'] = data['费率开仓'] + data['交易手续费额(元/手)']
    data['汇总平今手续费'] = data['平今'] + data["平今2"]
    data['投机买保证金'] = data['结算价'] * data['投机买保证金率(%)'] * data1['合约乘数'] / 100
    data['投机卖保证金'] = data['结算价'] * data['投机卖保证金率(%)'] * data1['合约乘数'] / 100
    data['涨停板'] = data1["最小变动单位"] * round((data['结算价'] * (1 + data2['涨停板幅度(%)'] / 100)) / data1['最小变动单位'])
    data['跌停板'] = data1["最小变动单位"] * round((data['结算价'] * (1 - data2['跌停板幅度(%)'] / 100)) / data1['最小变动单位'])

    a = data.loc[:, ["合约代码", "汇总开仓手续费", "汇总平今手续费", "投机买保证金", "投机卖保证金", '涨停板', '跌停板', '结算价']]
    a.to_dict()
    a.to_csv("arbitrage-trade/合约数据/汇总数据.csv", mode= 'a+')
    return a
tradeFee()
def tradeSymbol():
    syList = pd.read_csv("./合约数据/syList.csv")
    cu = syList.loc[1:12, ["成交手", "交割月份"]]
    # print(cu.sort_values(by=["交割月份","成交手"], ascending= [True, True]))
    bc = syList.loc[15:27, ["交割月份", "成交手"]]
    al = syList.loc[30:42, ["交割月份", "成交手"]]
    zn = syList.loc[45:57, ["交割月份", "成交手"]]
    pb = syList.loc[60:72, ["交割月份", "成交手"]]
    ni = syList.loc[75:87, ["交割月份", "成交手"]]
    sn = syList.loc[90:102, ["交割月份", "成交手"]]
    au = syList.loc[105:113, ["交割月份", "成交手"]]
    ag = syList.loc[116:128, ["交割月份", "成交手"]]
    rb = syList.loc[131:143, ["交割月份", "成交手"]]
    xc = syList.loc[146:158, ["交割月份", "成交手"]]
    hc = syList.loc[161:173, ["交割月份", "成交手"]]
    ss = syList.loc[176:188, ["交割月份", "成交手"]]
    sc = syList.loc[191:211, ["交割月份", "成交额"]]
    lu = syList.loc[214:226, ["交割月份", "成交手"]]
    fu = syList.loc[229:241, ["交割月份", "成交手"]]
    bu = syList.loc[244:256, ["交割月份", "成交手"]]
    ru = syList.loc[259:269, ["交割月份", "成交手"]]
    nr = syList.loc[272:284, ["交割月份", "成交手"]]
    sp = syList.loc[287:299, ["交割月份", "成交手"]]

    ls = [cu, bc, al, zn, pb, ni, sn, au, ag, rb, xc, hc, ss, sc, lu, fu, bu, ru, nr, sp]
    for i in range(len(ls)):
        ls[i].to_csv("./合约数据/symbol.csv", mode= 'a+')
    syls = pd.read_csv("./合约数据/symbol.csv")


def priceArg(**dataFile):
    # a = tradeFee()
    dict = {}
    tk1 = pd.read_csv(dataFile["file1"])
    tk2 = pd.read_csv(dataFile["file2"])
    tk3 = pd.read_csv("arbitrage-trade/合约数据/汇总数据.csv")
    symbol1 = tk1.iloc[1,0]
    symbol2 = tk2.iloc[1,0]
    mount1 = tk1.iloc[-1000:, 6]#成交总量
    mount2 = tk2.iloc[-1000:, 6]#成交总量
    turnOver1 = tk1.iloc[-1000:, 7] #成交总额1
    turnOver2 = tk2.iloc[-1000:, 7] #成交总额2
    aPri1 = tk1.iloc[-1000:,12] #卖一价
    bPri1 = tk1.iloc[-1000:,15]  #买一价
    aPri2 = tk2.iloc[-1000:, 12] #卖一价
    bPri2 = tk2.iloc[-1000:, 15] #买一价
    aSprPri = (aPri1.values - aPri2.values)[0:-1:20]
    bSprPri = (bPri1.values - bPri2.values)[0:-1:20]
    aSprAver = np.mean(aSprPri)
    bSprAver = np.mean(bSprPri)
    stdA = np.std(aSprPri,ddof=1)
    stdB = np.std(bSprPri,ddof=1)
    tickAver =np.mean((turnOver1 / mount1 / 5))
    
    #保证金计算
    BMargin1 = 43278
    SMargin1 = 43278
    BMargin2 = 43272
    SMargin2 = 43272
    margin1 = 0
    margin2 = 0
    if (BMargin1 > SMargin1):
        margin1 = BMargin1
    else:
        margin1 = SMargin1

    if (BMargin2 > SMargin2):
        margin2 = BMargin2
    else:
        margin2 = SMargin2


    argDict = {"合约代码1":symbol1, "合约代码2":symbol2, "Ask价差均值": aSprAver, "Bid价差均值": bSprAver, 
                "标准差A":stdA, "标准差B": stdB, "tick均值": tickAver, "保证金1": margin1, "保证金2": margin2}
    return argDict

def toJson(**argDict):
    with open('config.json','r') as jsonFile:
        load = json.load(jsonFile)
        loaded = load["list"]
        print(len(loaded))
        for i in range(len(loaded)):
            #放入列表中
            loaded[i]["ticker1"] = argDict["合约代码1"]
            loaded[i]["ticker2"] = argDict["合约代码2"]

            loaded[i]["aSprAver"] = argDict["Ask价差均值"]
            loaded[i]["bSprAver"] = argDict["Bid价差均值"]
            
            loaded[i]["stdA"] = argDict["标准差A"]
            loaded[i]["stdB"] = argDict["标准差B"]
            loaded[i]["tickAver"] = argDict["tick均值"]
            loaded[i]["保证金1"] = argDict["margin1"]
            loaded[i]["保证金2"] = argDict["margin2"]

            loaded[i]["hisOrderStatus1"]["total_amount"] = 20000
            loaded[i]["hisOrderStatus1"]["total_volume"] = -4
            loaded[i]["hisOrderStatus1"]["fee"] = a["open"][1]

            loaded[i]["hisOrderStatus2"]["total_amount"] = 20000
            loaded[i]["hisOrderStatus2"]["total_volume"] = 4
            loaded[i]["hisOrderStatus2"]["fee"] = a["open"][2]

    with open("config.json","w") as jsonFile:
        a = json.dump(loaded, jsonFile, indent= 4)

dataList = [dataFile1, dataFile2, dataFile3, dataFile4, dataFile5, dataFile6,
            dataFile7, dataFile8, dataFile9, dataFile10, dataFile11, dataFile12]

argList = []
for i in range(len(dataList)):
    argList[i] = priceArg(**dataList[i])
    toJson(**argList[i])

def firstPrice():#long period track
    # api = TqApi(TqKq(), auth= TqAuth("15221624883", "15221shuai"))
    tick_size = 10
    tk1 = pd.read_csv(dataFile1["file1"])
    tk2 = pd.read_csv(dataFile1["file2"])
    aPri1 = tk1.iloc[-3600:,12] 
    aPri2 = tk2.iloc[-3600:, 12]
    aSprPri = (aPri1.values - aPri2.values)\
    #bSprPri =
    
    adf1 = st.adfuller(np.diff(aPri1))  # 一阶差分ADF1%检测
    adf2 = st.adfuller(np.diff(aPri2))  
    adf3 = st.adfuller(aSprPri)
    if adf1[0] < adf1[4]['1%'] and adf2[0] < adf2[4]['1%']:
        cov = st.coint(aPri1, aPri2)
        print(cov)
        cov_t = cov[0]  #t
        cov_p = cov[1]  #p
        if cov_t < cov[2][0]:  # 协整1%置信度
            print("t<1%") 
        elif(cov_t < cov[2][1]):
            print("t<5%")
        elif(cov_t < cov[2][2]):
            print("t<10%")
        upPrice = np.percentile(aSprPri, 75)
        midPrice = np.percentile(aSprPri, 50)                                                                              
        downPrice = np.percentile(aSprPri, 25)
        print(upPrice, midPrice, downPrice)
        if ((upPrice - downPrice) <= tick_size):
            triOpen1 = midPrice + tick_size
            triOpen2 = midPrice - tick_size
        else:
            triOpen1 = upPrice
            triOpen2 = downPrice
    else:
        print("not passed test!")
firstPrice()
#0323





