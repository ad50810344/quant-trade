from datetime import date
import pandas as pd

def tradeFee():
    #手续费计算
    data = pd.read_csv("data.csv")

    data['费率开仓'] = data["交易手续费率(‰)"] * data["结算价"] / 100
    data["平今"] = data['费率开仓'] * data['平今折扣率(%)'] / 100
    data["平今2"] = data['交易手续费额(元/手)'] * data['平今折扣率(%)'] / 100
    data['open'] = data['费率开仓'] + data['交易手续费额(元/手)']
    data['closeToday'] = data['平今'] + data["平今2"]
    # data.to_csv("data.csv")
    # data.drop(data.columns[0],axis=1, inplace= True)
    a = data.loc[:, ["合约代码", "open", "closeToday"]]
    a.to_dict()
    print(a)
    a.to_csv("fee.csv", mode= 'a+')

def tradeSymbol():
    syList = pd.read_csv("syList.csv")
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
        ls[i].to_csv("symbol.csv", mode= 'a+')
    syls = pd.read_csv("symbol.csv")
    
tradeFee()
tradeSymbol()

