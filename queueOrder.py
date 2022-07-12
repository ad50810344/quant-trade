from cmath import nan
from time import time
from matplotlib import dates
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def orderAnalyse(file, fileOrderQueue, legA:str="", legB:str=""):
    import os
    # flog = os.getcwd() + "/logs"
    # if os.path.isfile(flog) != True:
    #     p = Path(flog)
    #     p.mkdir(exist_ok=True)

    # file = "/home/du/order_queue.csv"
    # datas = pd.read_csv(file)
    # firstRun =datas[0:40]
    # secondRun = datas[41:77]
    # print(secondRun)
    # norepeat_df = firstRun.drop_duplicates(subset=['order_id'], keep=False)
    # print(norepeat_df)
    datas = pd.read_csv(file)
    dataOrderQueue = pd.read_csv(fileOrderQueue)
    firstRun =datas
    allTradedDf = firstRun[firstRun["price"] != 0].drop(columns=["user_id", "user_virtual", "duration", "error"])
    df = allTradedDf.reset_index(drop=True).sort_values(["order_id"], ignore_index=True)
    
    tradeNums = len(df)
    closeProfit = []
    direction = []
    openPrice = []

    multi = 15
    for i, row in df.iterrows():
        if row["offset"] == "OPEN":
            if row["side"] == "SELL":
                if row["ticker"] == legA:
                    j = 0
                    while (j<=(len(df.iloc[i:len(df),]["status"].tolist())-1)):#最后一行无法超出
                        if df.iloc[(i+j)]["status"] == "ALL_TRADED" and df.iloc[(i+j)]["ticker"] == legB: 
                            openpriceB = df.iloc[i+1:(i+j+1),]["price"].mean()
                            openprice = row["price"] - openpriceB
                            break
                        elif df.iloc[(i+j)]["status"] == "NONE":
                            print("exception")    
                        j += 1
                    direct = "openShort"
                else:
                    openprice = 0
                    direct = "openLong"
            elif row["side"] == "BUY":
                if row["ticker"] == legA:
                    j = 0
                    while (j<=(len(df.iloc[i:len(df),]["status"].tolist())-1)):
                        if df.iloc[(i+j)]["status"] == "ALL_TRADED" and df.iloc[(i+j)]["ticker"] == legB:
                            openpriceB = df.iloc[i+1:i+j+1,]["price"].mean()
                            openprice = row["price"] - openpriceB
                            break    
                        elif df.iloc[(i+j)]["status"] == "NONE":
                            print("exception,legB has none orders")    
                        j += 1
                    direct = "openLong"
                else:
                    openprice = 0
                    direct = "openShort"
            profit = 0
        else:
            # k = 0
            profit = 0
            leng = len(df.iloc[0:i,]["ticker"].tolist())
            while(leng > 0):
                if df.iloc[(leng-1)]["ticker"] == row["ticker"] and df.iloc[(leng-1)]["side"] != row["side"]\
                    and df.iloc[(leng-1)]["offset"] != row["offset"]:
                    if row["side"] == "BUY":
                        # openprice = float(df.iloc[leng-1])
                        subprofit = (float(df.iloc[(leng-1)]["price"]) - float(row["price"])) * float(row["quantity"]) 
                    else:
                        subprofit = (float(row["price"]) - float(df.iloc[(leng-1)]["price"])) * float(row["quantity"])
                    break

                else:
                    pass
                # k += 1
                leng -= 1
            profit += subprofit * multi

            if row["side"] == "BUY":
                if row["ticker"] == legA:
                    direct = "closeShort"
                else:
                    direct = "closeLong"
            else:
                if row["ticker"] == legA:
                    direct = "closeLong"
                else:
                    direct = "closeShort"

        closeProfit.append(profit)
        direction.append(direct)
        openPrice.append(openprice)
    df["closeProfit"] = closeProfit
    df["direction"] = direction
    df["openPrice"] = openPrice
    return df, dataOrderQueue


def getCsv(fileticker):
    quotedata = pd.read_csv(fileticker)
    return quotedata.drop(columns=["昨收价", "开盘价", "收盘价", "最新价","成交总量",\
                            "成交总额","持仓量","最高价","最低价","成交笔数",\
                            "买进总笔数1","卖出总笔数1","Unnamed: 18"])


def getQuote(filelist, df):
    lessTicker = getCsv(filelist[0])
    lessTicker2 = getCsv(filelist[1])
    lessTicker.to_csv("zhubiticker1.csv")
    bidPrice = []
    askPrice = []

    samebid = []
    sameask = []
    if len(lessTicker) >= len(lessTicker2):
        for i in lessTicker2["时间"].tolist():
            if i in lessTicker["时间"].tolist():
                bid1 = lessTicker[lessTicker["时间"] == i]["买价1"].tolist()[0]
                ask1 = lessTicker[lessTicker["时间"] == i]["卖价1"].tolist()[0]
                samebid.append(bid1)
                sameask.append(ask1)
        sprB = [lessTicker2["买价1"].tolist() - int(samebid[i]) for i in range(len(samebid))]
        sprA = [lessTicker2["卖价1"].tolist() - int(sameask[i]) for i in range(len(sameask))]
    else:
        for i in lessTicker["时间"].tolist():
            if i in lessTicker2["时间"].tolist():
                bid1 = lessTicker2[lessTicker2["时间"] == i]["买价1"].tolist()[0]
                ask1 = lessTicker2[lessTicker2["时间"] == i]["卖价1"].tolist()[0]
                samebid.append(bid1)
                sameask.append(ask1)
        sprB = [lessTicker["买价1"].tolist() - int(samebid[i]) for i in range(len(samebid))]
        sprA = [lessTicker["卖价1"].tolist() - int(sameask[i]) for i in range(len(sameask))]


    plt.plot(np.arange(len(sprA)), sprA)
    plt.show()

# df = orderAnalyse(file, legA, legB)
# samebid, sameask = getQuote(filelist, df)

# print(sameask)
# plt.plot(np.arange(len(samebid)), samebid)
# plt.show()


def getspr(fileticker, df):
    lessTicker = getCsv(fileticker)
    lessTicker.to_csv("zhubiticker1.csv")
    bidPrice = []
    askPrice = []

    for i in df["time"].tolist():
        if int(i[20:23]) > 500:
            a = i.replace(i[19:31],'.500')
        elif int(i[20:23]) >= 000 and int(i[20:23]) <= 500:
            a = i.replace(i[19:31],'.000')        
        formtime = a.replace(a[10],'~')
        if formtime in lessTicker["时间"].tolist():
            bidprice = lessTicker[lessTicker["时间"] == formtime]["买价1"].tolist()[0]
            askprice = lessTicker[lessTicker["时间"] == formtime]["卖价1"].tolist()[0]
        else:
            bidprice = 0
            askprice = 0
        bidPrice.append(bidprice)    
        askPrice.append(askprice)    
    # i = 0
    # while (i<len(index1)-1):
    #     data = pd.read_csv(fileticker)
    #     print(data.loc[index1[i]:index1[i+1]])
    #     print("ok")
    #     i += 1
    return bidPrice, askPrice
        

def fmttime(t3, data2):
    if int(t3[20:23]) > 500:
        a = t3.replace(t3[19:31],'.500')
    elif int(t3[20:23]) >= 000 and int(t3[20:23]) <= 500:
        a = t3.replace(t3[19:31],'.000')        
    fmtime3 = a.replace(a[10],'~')
    if fmtime3 in data2["时间"].tolist():
        num2 = data2[data2["时间"] == fmtime3].index.values[0]
    return num2

def addSerial():
    df, dfQueue = orderAnalyse(file, fileOrderQueue, legA, legB)
    bidPriceLegA, askPriceLegA = getspr(fileticker, df)
    bidPriceLegB, askPriceLegB = getspr(fileticker2, df)
    sprB = [int(bidPriceLegA[i]) - int(bidPriceLegB[i]) for i in range(len(bidPriceLegA))]
    sprA = [int(askPriceLegA[i]) - int(askPriceLegB[i]) for i in range(len(askPriceLegA))]
    # for i in range(len(sprA)):
    #     if sprA[i] == 0:
    #         sprA[i] = sprA[i+3]
    #         print(sprA[i])
    df["bP1"] = bidPriceLegA
    df["aP1"] = askPriceLegA
    df["bP2"] = bidPriceLegB
    df["aP2"] = askPriceLegB
    df["sprB"] = sprB
    df["sprA"] = sprA

    #平仓成本--平仓盈利一组
    sumclose = []
    data = pd.read_csv(fileticker)
    data2 = pd.read_csv(fileticker2)
    cancelB = 0
    noCancelB = 0
    floatMinAtick = []
    floatMaxAtick = []
    floatLastAtick = []

    tempFloatAtick = []
    profitSellA = []
    profitBuyA = []

    for i, row in df.iterrows():
        if row["ticker"] == legA:
            if row["direction"] == "closeShort" or row["direction"] == "closeLong":
                n = 0
                while (n<=(len(df.iloc[i:len(df),]["direction"].tolist())-1)):
                    if df.iloc[(i+n)]["direction"] == "openShort" or df.iloc[(i+n)]["direction"] == "openLong":
                        sum = df.iloc[(i):(i+n+1)]["closeProfit"].sum()
                        # m = 0
                        # while (m<=i):
                        #     if df.iloc[(i-m-1)]["direction"] == "openLong" or\
                        #         df.iloc[(i-m-1)]["direction"] == "openShort":
                        #         row["openPrice"] =  int(df.iloc[i-m-1]["openPrice"]) - (sumprofit/int(df.iloc[i-m-1]["quantity"]))
                        #         break                         
                        break
                    n += 1
                sumclose.append(sum)  

            t = row["time"]
            if int(t[20:23]) > 500:
                a = t.replace(t[19:31],'.500')
            elif int(t[20:23]) >= 000 and int(t[20:23]) <= 500:
                a = t.replace(t[19:31],'.000')        
            fmtime = a.replace(a[10],'~')
            if fmtime in data["时间"].tolist():
                num1 = data[data["时间"] == fmtime].index.values[0]
            else:
                print("数据源错误，无法读取")
            # index1.append(num1)

            m = 0
            while (m<=(len(df.iloc[i:len(df),]["ticker"].tolist())-1)):
                if df.iloc[(i+m)]["ticker"] == legB:                    
                    t2 = df.iloc[i+1,:]["time"]
                    if int(t2[20:23]) > 500:
                        a = t2.replace(t2[19:31],'.500')
                    elif int(t2[20:23]) >= 000 and int(t2[20:23]) <= 500:
                        a = t2.replace(t2[19:31],'.000')        
                    fmtime2 = a.replace(a[10],'~')
                    if fmtime2 in data2["时间"].tolist():
                        num2 = data2[data2["时间"] == fmtime2].index.values[0]
                    if fmtime2 in data["时间"].tolist():
                        num1last = data[data["时间"] == fmtime2].index.values[0]
                    break
                m += 1

            if row["side"] == "SELL":
                sellA = data.iloc[num1:(num1last+1),:]["卖价1"].tolist()
                if sellA:
                    for j in range(len(sellA)):
                        floatA = row["price"] - sellA[j]
                        profitSellA.append(floatA)
                    minFloatA = min(profitSellA)
                    maxFloatA = max(profitSellA)
                    lastFloatA = profitSellA[-1]
                else:
                    minFloatA = 0
            elif row["side"] == "BUY":
                buyA = data.iloc[num1:(num1last+1),:]["买价1"].tolist()
                if buyA:
                    for j in range(len(buyA)):
                        floatA = buyA[j] - row["price"]
                        profitBuyA.append(floatA) #A腿成交后波动情况列表
                    minFloatA = min(profitBuyA)
                    maxFloatA = max(profitBuyA)
                    lastFloatA = profitBuyA[-1]
                else:
                    minFloatA = 0

            if minFloatA <= -2:
                cancelB += 1
            else:
                noCancelB += 1

            floatMinAtick.append(minFloatA)
            floatMaxAtick.append(maxFloatA)
            floatLastAtick.append(lastFloatA)
            tempFloatAtick.append(minFloatA)
        else:
            minFloatA = nan
            floatMinAtick.append(minFloatA)
    df["floatAtick"] = floatMinAtick


    profitB = []
    maxProfitB = []
    for i, row in dfQueue.iterrows():
        if row["ticker"] == legB and row["type"] == "insert":
            n = 0
            while (n<=(len(dfQueue.iloc[i:len(dfQueue),:]["type"].tolist())-1)):
                if dfQueue.iloc[(i+n)]["type"] == "cancel" and dfQueue.iloc[(i+n),:]["ticker"] == legB:
                    insertBtime = dfQueue.iloc[(i+n-1),:]["time"]  #insertBtime
                    cancelBtime = dfQueue.iloc[(i+n),:]["time"]    #cancelBtime
                    numInsertB = fmttime(insertBtime, data2)
                    numCancelB = fmttime(cancelBtime, data2)
                    break
                n += 1
            if dfQueue.iloc[(i+n-1),:]["side"] == "SELL":
                sellB = data2.iloc[numInsertB:(numCancelB+1),:]["卖价1"].tolist()
                if sellB:
                    for j in range(len(sellB)-1):
                        FloatB = int(dfQueue.iloc[(i+n-1),:]["price"]) - sellB[j]
                        profitB.append(FloatB) #正确
                    maxFloatB = max(profitB)
                else:
                    maxFloatB = 0
            elif dfQueue.iloc[(i+n-1),:]["side"] == "BUY":
                buyB = data2.iloc[numInsertB:(numCancelB+1),:]["买价1"].tolist()
                if buyB:
                    for j in range(len(buyB)-1):
                        FloatB = buyB[j] - int(dfQueue.iloc[(i+n-1),:]["price"])
                        profitB.append(FloatB)
                    maxFloatB = max(profitB)
                else:
                    maxFloatB = 0   
            maxProfitB.append(maxFloatB) #计算出结果似乎有问题
    df.to_csv("zhubi.csv")



    #交易次数/盈亏比/胜率/单次最大亏损/单次最大盈利/A腿成交前价差/B腿成交时价差
    print("开始时间:",df["time"].iloc[0])
    print("结束时间:",df["time"].iloc[-1])

    totalProfit = df["closeProfit"].sum() #总盈亏
    totalProfitF = "%.2f" % totalProfit

    tradeNum = len(df)  #交易次数

    fee = 3.63 * tradeNum

    netProfit = float(totalProfitF) - fee
    
    # profit = df[df["closeProfit"] > 0]
    # loss = df[df["closeProfit"] < 0]
    # winratio = len(profit)/(len(profit)+len(loss))
    # winRatio = "%.2f%%" % (winratio * 100) #胜率
    # print("胜率:",winRatio)

    maxProfit = max(sumclose)#单次最大盈利
    maxProfitF = "%.2f" % maxProfit
    id1 = sumclose.index(maxProfit)

    maxLoss = min(sumclose)#单次最大亏损
    maxLossF = "%.2f" % maxLoss
    id2 = sumclose.index(maxLoss)
    
    wintrade = 0
    losstrade = 0
    win = 0
    loss = 0
    for i in range(len(sumclose)):
        if sumclose[i] > 0:
            wintrade += 1
            win += sumclose[i]
        else:
            losstrade += 1
            loss += sumclose[i]
    winratio = wintrade/(wintrade+losstrade)
    yingkuibi = (win/wintrade)/(loss/losstrade)
    winRatio = "%.2f%%" % (winratio * 100) #胜率

    print("平仓盈亏:",totalProfitF)
    print("平均每组盈利:",win/wintrade)
    print("平均每组亏损:",loss/losstrade)
    print("总交易次数:",tradeNum)
    print("盈利比例：",winRatio)
    print("手续费：",round(fee,2))
    print("净盈亏：",round(netProfit,2))
    print("单次最大盈利:", maxProfitF)
    print("单次最大亏损:", maxLossF)
    print("B撤单重报:",cancelB/(cancelB+noCancelB))

    # print("A腿成交后最大浮亏tick:",tempFloatAtick)
    print("A腿成交后最大浮亏tick出现次数:")
    print(pd.value_counts(tempFloatAtick))
    # print("A腿成交后最大浮盈tick:",floatMaxAtick)
    print("A腿成交后最大浮盈tick出现次数:")
    print(pd.value_counts(floatMaxAtick))
    # print("B腿成交时A腿浮盈tick:",floatLastAtick)
    print("B腿成交时A腿浮盈tick出现次数:")
    print(pd.value_counts(floatLastAtick))

    print("B腿挂单浮动盈亏最大tick:")
    print(pd.value_counts(maxProfitB))
    print("每组套利平仓盈亏：",sumclose)
    
    #B腿500毫秒内最大变化程度，撤除原本的挂单，fak报出，撤单限制2个tick
    
    #A腿成交前价差/B腿成交时价差

    # profit_buy = profit[profit["多/空"] == "多"]
    # profit_sell = profit[profit["多/空"] == "空"]
    # loss = datas[datas["closeProfit"] <= 0]
    # loss_buy = loss[loss["多/空"] == "多"]
    # loss_sell = loss[loss["多/空"] == "空"]
    # print(profit,loss,sep="\n")
    # print(profit.describe(),loss.describe(),sep="\n")
    # print("胜率",len(profit)/len(datas))
    # print("盈亏额比例",abs(profit["盈利金额"].sum()/loss["盈利金额"].sum()),"平均盈亏额比例",abs(profit["盈利金额"].mean()/loss["盈利金额"].mean()))
    
    # mean5 = []
    # count_mean5 = []
    # for i in datas["盈利点数"].rolling(5):
    #     mean5.append(len(i[i > 0])/len(i)) 
    #     if list(i[i > 0]):
    #         count_mean5.append(i[i > 0].mean()) 
    #     else:count_mean5.append(0.0)
    # win_rate5 = pd.Series(mean5,name="5日胜率")
    # profit_count_mean5 = pd.Series(count_mean5,name="5日平均盈利点数")
    # print("5日胜率均值",win_rate5.mean(),"5日胜率标准差",win_rate5.std())
    # print("5日平均盈利点数均值",profit_count_mean5.mean(),"5日平均盈利点数标准差",profit_count_mean5.std())
    # figure, ax = plt.subplots(2,1)
    # win_rate5.plot(figure=figure, ax=ax[0], title="5日胜率")
    # profit_count_mean5.plot(figure=figure, ax=ax[1], title="5日平均盈利点数")
    # plt.show()

    # x= np.arange(len(df))
    # plt.plot(df["order_id"].tolist(), df["bP1"].tolist())
    # plt.show()

legA = "ag2208.SHFE"
legB = "ag2212.SHFE"
file = "/home/du/yd/20220531/order_status.csv"
fileOrderQueue = "/home/du/yd/20220531/order_queue.csv"
fileticker = "/home/du/yd/20220525/ag2212.SHFE-2022-0525-y.csv"
fileticker2 = "/home/du/yd/20220525/ag2206.SHFE-2022-0525-y.csv"
# filelist = [fileticker, fileticker2]
addSerial()
