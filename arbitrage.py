# encoding: UTF-8
from cmath import isinf, isnan
from fileinput import lineno
from math import ceil, floor
from optparse import Values
from ctaBase import *
from ctaTemplate import *
import time
import random
from enum import Enum

class PosStatus(object):
    def __init__(self, value):
        self.Value = value
        
    def isEmpty(self):
        return self.Value == 0 

    def isLong(self):
        return (self.Value & 3) == 1

    def isShort(self):
        return (self.Value & 3) == 3
    
    def isBalance(self):
        return self.Value < 5
    
    class Value(Enum):
        Empty = 0
        Long = 1
        Short = 3
        LongPartialLong = 5
        ShortPartialLong =7
        LongPartialShort = 13
        ShortPartialShort = 15

Action = ['OpenLong', 'OpenShort', 'CloseLong', 'CloseShort', 'Empty']

class Profit():
    def __init__(self):
        self.profit = 0
        self.fee = 0
        self.rhs = 0

    def __add__(self):
        pass


class Strategy_Arbitrage(CtaTemplate):
    vtSymbol = ''
    exchange = ''
    className = 'Strategy_Arbitrage'
    author = 'dushuai'
    name = EMPTY_UNICODE # 策略实例名称

    # 参数映射表
    paramMap = {
        'P': '触发价格',
        'V': 'lot',
        'exchange': '交易所',
        'vtSymbol': '合约'
    }
    # 参数列表，保存了参数的名称
    paramList = list(paramMap.keys())

    # 变量映射表
    varMap = {
        'trading': '交易中',
        'pos': '仓位'
    }
    # 变量列表，保存了变量的名称
    varList = list(varMap.keys())


    def __init__(self,ctaEngine=None,setting={}):
        super().__init__(ctaEngine, setting)
        self.output("初始化变量")
        self.P = 4720                            # 买入触发价
        self.V = 10                               # 下单手数
        self.output(time.asctime(time.localtime(time.time())))
        self.output(random.random())

        # 注意策略类中的可变对象属性（通常是list和dict等），在策略初始化时需要重新创建，
        # 否则会出现多个策略实例之间数据共享的情况，有可能导致潜在的策略逻辑错误风险，
        # 策略类中的这些可变对象属性可以选择不写，全都放在__init__下面，写主要是为了阅读
        # 策略时方便（更多是个编程习惯的选择）        

        self.running = True
        self.ticker1 = ''; self.ticker2 = ''
        self.bPrice1=0; self.bPrice2=0; self.aPrice1=0; self.aPrice2=0; self.lPrice1=0; self.lPrice2 = 0 
        self.time1=0; self.time2 = 0
        self.orderData = 0
        self.startPairCouter = 0
        self.orderId1 = []
        self.orderId2 = []
        self.finishFlag1 = []
        self.finishFlag2 = []
        self.closeProfit1 = []
        self.closeProfit2 = []
        self.finishOffset1=0; self.finishOffset2 = 0
        self.openOffset1=-1; self.openOffset2 = -1
        self.openOffsetQuantity1=0; self.openOffsetQuantity2 = 0
        self.OrderStatus1 = VtTradeData()
        self.OrderStatus2 = VtTradeData()
        self.offsets = []
        self.pairProfits = []
        self.nearPairProfits = []
        self.maPairProfits = []

        self.closeProfit = Profit()
        self.openProfit = Profit()
        self.avgOpenAmount1=0; self.avgOpenAmount2 = 0
        self.avgOpenFee1=0; self.avgOpenFee2 = 0
        self.cancelCount1=0; self.cancelCountFak2=0; self.cancelCountLimit2=0; self.reInsertOrderB = 0
        self.allTradedCount1=0; self.allTradedCount2 = 0
        self.cancelRatio1=0; self.cancelRatio2 = 0
        self.onPriceCount1=0; self.onPriceCount2 = 0
        self.betterPriceCount1=0; self.betterPriceCount2 = 0
        self.onPriceRatio1=0; self.onPriceRatio2 = 0
        self.gainPairCount=0; self.lossPairCount = 0
        
        self.openProfitStopLoss = 0
        self.stoploss = 0

        self.longPositionToday1=0; self.longPositionHis1=0; self.shortPositionToday1=0; self.shortPositionHis1 = 0
        self.longPositionToday2=0; self.longPositionHis2=0; self.shortPositionToday2=0; self.shortPositionHis2 = 0
        self.status = PosStatus(0) #wrong
        self.quantity = 0
        self.sumQuantity = 1; self.sumQuantity1=0; self.sumQuantity2 = 0
        self.price1=0; self.price2 = 0
        self.ATickSerialAskP=[]; self.BTickSerialAskP=[]; self.ATickSerialBidP=[]; self.BTickSerialBidP = []
        self.sprAverSerial = []
        self.closeSpr = []
        self.sprAver = 0
        self.downOpenLong = 2; self.upOpenShort = 2; self.downCloShort = 1; self.upCloLong = 1

        self.amount1=0; self.amount2=0; self.LTickAver = 0
        self.volume1=0; self.volume2 = 0

        self.tick_size1=0; self.tick_size2 = 0
        self.aSprAver=0; self.bSprAver=0; self.stdA=0; self.stdB=0; self.tickAver = 0
        self.margin1=0; self.margin2 = 0
        self.cancelLimit1=0; self.cancelLimit2 = 0
        self.strategyPosition=0; self.maxPosition=0; self.initLot=0; self.maxLot=0; self.loopCount=0; self.loopInterval = 0
        self.contractMulti1=0; self.contractMulti2=0; self.stopLimitPrice = 0
        self.strategyCapiRatio = 0
        self.overPriSum=0; self.overPriceA=0; self.overPriceB = 0
        self.marginRatio1=0; self.marginRatio2 = 0
        self.position1=0; self.position2 = 0
        self.loopNum = 0
        self.ATime=[]; self.BTime = []
        self.cancelAInterval = []
        self.ATickInterval=[]; self.ATickInterval2 = 0
        self.cancelAv=[]; self.cancelAv2 = []
        self.cancelASpeed = 0
        self.moveShort=0; self.moveLong = 0
        
    def pairTrader(self):
        asset = self.get_investor_account()
        if self.margin1 < self.margin2:
            margin = self.margin1
        else:
            margin = self.margin2
        self.maxPosition = int((asset.available * self.strategyCapiRatio)/margin)
        self.cancelASpeed = 0

    def setOrderData(self, data:int):
        self.orderData = data

    def getTickers(self):
        tickerList = [self.ticker1, self.ticker2]
        return tickerList

    def isBalancedAndFinished(self):
        return self.status.isBalance and self.finishOffset1 == len(self.orderId1) and self.finishOffset2 == len(self.orderId2)

    def quantile(self, x:list, q:int):
        assert(q >= 0.0 and q <= 1.0)
        id = (len(x) -1) * q
        qs = x[floor(id)]
        h = id - floor(id)
        return (1.0 - h) * qs + h * x[ceil(id)]

    def onTick(self, tick):
        super().onTick(tick)
        self.output("进入onTick")
        if (self.running):
            self.output('return')
            return 0

        if tick == self.ticker1:
            self.aPrice1 = tick.askPrice1
            self.bPrice1 = tick.bidPrice1
            self.lPrice1 = tick.lastPrice
            self.time1 = tick.time
            self.amount1 = tick.turnover
            self.volume1 = tick.volume
        elif tick == self.ticker2:
            self.aPrice2 = tick.askPrice1
            self.bPrice2 = tick.bidPrice1
            self.lPrice2 = tick.lastPrice
            self.time2 = tick.time
            self.amount2 = tick.turnover
            self.volume2 = tick.volume
        else:
            return 0

        if abs(self.time1 - self.time2) < 50 * 1000 * 1000:
            if len(self.ATickSerialAskP) < 20 and len(self.BTickSerialAskP) < 20:
                self.ATickSerialAskP.append(self.aPrice1)
                self.BTickSerialAskP.append(self.aPrice2)
                self.ATickSerialBidP.append(self.bPrice1)
                self.BTickSerialBidP.append(self.bPrice2)
            else:
                self.aSprAver = self.aSprAver * 0.98 + (self.ATickSerialAskP[-1] - self.BTickSerialAskP[-1]) * 0.02
                self.bSprAver = self.bSprAver * 0.98 + (self.ATickSerialBidP[-1] - self.BTickSerialBidP[-1]) * 0.02
                self.ATickSerialAskP.clear()
                self.ATickSerialBidP.clear()
                self.BTickSerialAskP.clear()
                self.BTickSerialBidP.clear()
            self.sprAver = int(((self.aSprAver + self.bSprAver) * 0.5 / self.tick_size1) * self.tick_size1)
            if len(self.sprAverSerial) < 180:
                self.sprAverSerial.append(self.sprAver)
            else:
                upSprAver = int(self.quantile(self.sprAverSerial, 0.15))
                downSprAver = int(self.quantile(self.sprAverSerial, 0.85))
                if upSprAver >= self.sprAverSerial[-1] + self.upOpenShort:
                    self.upOpenShort = upSprAver - self.sprAverSerial[-1]
                if downSprAver <= self.sprAverSerial[-1] + self.downOpenLong:
                    self.downOpenLong = self.sprAverSerial[-1] + downSprAver
                self.sprAverSerial.clear()
            lastSprAsk = self.aPrice1 - self.aPrice2
            lastSprBid = self.bPrice1 - self.bPrice2
        
            longPos1 = self.longPositionHis1 + self.longPositionToday1
            shortPos1 = self.shortPositionHis1 + self.shortPositionToday1
            longPos2 = self.longPositionHis2 + self.longPositionToday2
            shortPos2 = self.shortPositionHis2 + self.shortPositionToday2
            ratio = 1
            openProfit1 = 0
            openProfit2 = 0
            effPostion = 0
            if longPos1 > 0:
                assert(shortPos1 == 0 and longPos2 == 0)
                openProfit1 = self.aPrice1 * longPos1 * self.contractMulti1 - self.avgOpenAmount1
                openProfit2 = self.avgOpenAmount2 - self.aPrice2 * shortPos2 * self.contractMulti2
                ratio = float(longPos1) / float(shortPos2)
                effPostion = longPos1
            else:
                openProfit1 = self.avgOpenAmount1 - self.bPrice1 * shortPos1 * self.contractMulti1
                openProfit2 = self.bPrice2 * longPos2 * self.contractMulti2 - self.avgOpenAmount2
                ratio = float(shortPos1) / float(longPos2)
                effPostion = -longPos1

            if isnan(ratio):
                self.openProfit = Profit(0, 0)
            elif isinf(ratio):
                self.openProfit = Profit(openProfit1, self.avgOpenFee1)
            else:
                self.openProfit = Profit(openProfit1 + ratio * openProfit2, self.avgOpenFee1 + ratio * self.avgOpenFee2)
            
            self.openProfitStopLoss = self.stoploss * self.tick_size1 * self.contractMulti1
            if self.openProfit.profit >= abs(effPostion) * self.openProfitStopLoss:
                self.quantity = 1
                if effPostion == 0:
                    self.closeSpr.append(self.sprAver)
                    if lastSprAsk >= (self.closeSpr[-1] + self.upOpenShort + self.moveShort) * self.tick_size1:
                        side = Action['OpenShort']
                        if abs(effPostion) < self.maxPosition:
                            self.ATickInterval += 1
                        if self.cancelASpeed > 50:
                            self.moveShort = 1
                            if abs(self.aPrice1 - self.bPrice1) > 1:
                                self.price1 = self.aPrice1 + 1 * self.tick_size1
                            else:
                                self.price1 = self.aPrice1 + self.tick_size1 #sendSellA
                            self.price2 = self.aPrice2
                        else:
                            if abs(self.aPrice1 - self.bPrice1) > 1:
                                self.price1 = self.aPrice1 + 0 * self.tick_size1
                            else:
                                self.price1 = self.aPrice1 + 0 * self.tick_size1
                            self.price2 = self.aPrice2
                    elif lastSprBid <= (self.closeSpr[-1] + self.downOpenLong + self.moveLong) * self.tick_size1:
                        side = Action['OpenLong']
                        if abs(effPostion) < self.maxPosition:
                            self.ATickInterval += 1
                        if self.cancelASpeed > 50:
                            self.moveLong = -1
                            if abs(self.aPrice1 - self.bPrice1) > 1:
                                self.price1 = self.bPrice1 + 1 * self.tick_size1
                            else:
                                self.price1 = self.bPrice1 + self.tick_size1 #sendBuyA
                            self.price2 = self.bPrice2
                        else:
                            if abs(self.aPrice1 - self.bPrice1) > 1:
                                self.price1 = self.bPrice1 - 0 * self.tick_size1
                            else:
                                self.price1 = self.bPrice1 - 0 * self.tick_size1
                            self.price2 = self.bPrice2
                    else:
                        side = Action['Empty']
                        return 0
                elif effPostion > 0:
                    self.output("effPostion > 0")
                    pass    #waiting
                elif effPostion < 0:
                    self.output("effPostion < 0")
                    pass
            else:
                if effPostion > 0:
                    side = Action['CloseLong']
                    self.price1 = self.aPrice1 - 3 * self.tick_size1
                    self.price2 = self.aPrice2
                else:
                    side = Action['CloseShort']
                    self.price1 = self.bPrice1 + 3 * self.tick_size1
                    self.price2 = self.bPrice2

            holdATicks = 0
            cancelFlag = False
            for i in range(self.finishOffset1, len(self.orderId1)):
                o = self.onOrder()


        # 过滤涨跌停和集合竞价
        if tick.lastPrice == 0 or tick.askPrice1==0 or tick.bidPrice1==0:
            return
        if tick.lastPrice > self.P:
            self.orderID = self.buy(tick.askPrice1, self.V)


    def onTrade(self, trade):
        super().onTrade(trade, log=True)
        self.output(trade.tradeTime)


    def onStart(self):
        super().onStart()
