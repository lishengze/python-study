# -*- coding: UTF-8 -*-

import time
import pickle
from QtAPI import *
from QtDataAPI import *

g_BeatInterval = 5  # 运行信号输出间隔
g_cycle    = False  # Demo程序是否持续运行

g_toScreen = False  # 提取的数据是否输出到屏幕
g_toFile   = True   # 提取的数据是否输出到文件

g_StsFreq     = 60  # 订阅的分时数据频率，单位: 秒
g_StsLeft     = 10  # 示例程序只接收一定数量行情即退出
g_L2QuoteLeft = 30
g_L1QuoteLeft = 30

g_toGBK    = False  # 提取的数据是否进行汉字编码转换

# UTF-8转换为GBK编码
def ConvertStr(data):
    if ~g_toGBK:
        return data
    nLen = len(data)
    if nLen == 0:
        return data
    for col_name in data.columns:
        if type(data.ix[0, col_name]) == type('str'):
            for index, row in data.iterrows():
                data.ix[index,col_name] = data.ix[index,col_name].decode('UTF-8').encode('GBK')
    return data

# 提取用户和密码
# 返回值为：(ret, usr, pwd)
def GetUsrPwd(filename):
    if os.path.exists(filename):
        pass
    else:
        return (False, "", "")

    usr = None
    pwd = None
    f = open(filename, "r")

    line = f.readline()
    strs = line.split(':')
    if 0 == len(strs):
        f.close()
        return (False, "", "")
    usr = strs[1].strip()
    line = f.readline()
    strs = line.split(':')
    if 0 == len(strs):
        f.close()
        return (False, "", "")
    pwd = strs[1].strip()
    f.close()

    return (True, usr, pwd)

# 分时行情回调函数示例


class TestApi(object):
    def __init__(self):
        self.__name__ = "TestApi"
        self._ofilename_sts = 'DemoQuoteOut_Sts.txt'
        self._ofilename_l2 = 'DemoQuoteOut_L2.txt'
        self._ofilename_l1 = 'DemoQuoteOut_L1.txt'

    def OnSubSts(self, data):
        global g_StsLeft
        g_StsLeft -= 1
        dictDataStr = ''

        strBuyPrice = ", BuyPrice = "
        for iter in data.BuyPrice:
            strBuyPrice = strBuyPrice + str(iter) + ','

        strBuyVolume = ", BuyVolume = "
        for iter in data.BuyVolume:
            strBuyVolume = strBuyVolume + str(iter) + ','

        strSellPrice = ", SellPrice = "
        for iter in data.SellPrice:
            strSellPrice = strSellPrice + str(iter) + ','

        strSellVolume = ", SellVolume = "
        for iter in data.SellVolume:
            strSellVolume = strSellVolume + str(iter) + ','

        dictDataStr = ": Symbol = " + str(data.Symbol)\
        + ", TradingDate = " + str(data.TradingDate)\
        + ", TradingTime = " + str(data.TradingTime)\
        + ", UNIX = " + str(data.UNIX)\
        + ", Market = " + str(data.Market)\
        + ", OP = " + str(data.OP)\
        + ", HIP = " + str(data.HIP)\
        + ", LOP = " + str(data.LOP)\
        + ", CP = " + str(data.CP)\
        + ", CQ = " + str(data.CQ)\
        + ", CM = " + str(data.CM)\
        + ", Change = " + str(data.Change)\
        + ", ChangeRatio = " + str(data.ChangeRatio)\
        + ", TQ = " + str(data.TQ)\
        + ", Vwap = " + str(data.Vwap)\
        + ", OBPD = " + str(data.OBPD)\
        + ", ClvLOP = " + str(data.ClvLOP)\
        + ", ClvHIP = " + str(data.ClvHIP)\
        + ", ClvVwap = " + str(data.ClvVwap)\
        + ", ShortName = " + str(data.ShortName)\
        + ", Position = " + str(data.Position)\
        + ", ConSign = " + str(data.ConSign)\
        + ", Rtn = " + str(data.Rtn)\
        + ", ConSignName = " + str(data.ConSignName)\
        + ", Varieties = " + str(data.Varieties)\
        + ", MarginUnit = " + str(data.MarginUnit)\
        + ", MaintainingMargin = " + str(data.MaintainingMargin)\
        + strBuyPrice + strBuyVolume + strSellPrice + strSellVolume

        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S '
        localTime = time.strftime(ISOTIMEFORMAT, time.localtime())
        #print str(localTime), dictDataStr
        with open(self._ofilename_sts, 'a') as of:
            of.writelines("Sts: " + str(localTime) + ":" + dictDataStr + "\n")

        return

    # L2Quote行情回调函数示例
    def OnSubL2Quote(self, data):
        global  g_L2QuoteLeft
        g_L2QuoteLeft -= 1
        dictDataStr = ''

        strBuyPrice = ", BuyPrice = "
        for iter in data.BuyPrice:
            strBuyPrice = strBuyPrice + str(iter) + ','

        strBuyVolume = ", BuyVolume = "
        for iter in data.BuyVolume:
            strBuyVolume = strBuyVolume + str(iter) + ','

        strTotalBuyOrderNo = ", TotalBuyOrderNo = "
        for iter in data.TotalBuyOrderNo:
            strTotalBuyOrderNo = strTotalBuyOrderNo + str(iter) + ','

        strSellPrice = ", SellPrice = "
        for iter in data.SellPrice:
            strSellPrice = strSellPrice + str(iter) + ','

        strSellVolume = ", SellVolume = "
        for iter in data.SellVolume:
            strSellVolume = strSellVolume + str(iter) + ','

        strTotalSellOrderNo = ", TotalSellOrderNo = "
        for iter in data.TotalSellOrderNo:
            strTotalSellOrderNo = strTotalSellOrderNo + str(iter) + ','

        strBidImplyQty = ", BidImplyQty = "
        for iter in data.BidImplyQty:
            strBidImplyQty = strBidImplyQty + str(iter) + ','

        strAskImplyQty = ", AskImplyQty = "
        for iter in data.AskImplyQty:
            strAskImplyQty = strAskImplyQty + str(iter) + ','

        strBestBuyQty = ", BestBuyQty = "
        for iter in data.BestBuyQty:
            strBestBuyQty = strBestBuyQty + str(iter) + ','

        strBestSellQty = ", BestSellQty = "
        for iter in data.BestSellQty:
            strBestSellQty = strBestSellQty + str(iter) + ','

        dictDataStr = ": Symbol = " + str(data.Symbol)\
        + ", TradingDate = " + str(data.TradingDate)\
        + ", TradingTime = " + str(data.TradingTime)\
        + ", UNIX = " + str(data.UNIX)\
        + ", Market = " + str(data.Market)\
        + ", LCP = " + str(data.LCP)\
        + ", OP = " + str(data.OP)\
        + ", HIP = " + str(data.HIP)\
        + ", LOP = " + str(data.LOP)\
        + ", CP = " + str(data.CP)\
        + ", CP1 = " + str(data.CP1)\
        + ", TT = " + str(data.TT)\
        + ", TQ = " + str(data.TQ)\
        + ", TM = " + str(data.TM)\
        + ", BuyLevelNo = " + str(data.BuyLevelNo)\
        + strBuyPrice + strBuyVolume + strTotalBuyOrderNo \
        + strSellPrice + strSellVolume + strTotalSellOrderNo \
        + ", TBOVOL = " + str(data.TBOVOL) \
        + ", SellLevelNo = " + str(data.SellLevelNo)\
        + ", TSOVOL = " + str(data.TSOVOL)\
        + ", WAvgBP = " + str(data.WAvgBP)\
        + ", WAvgSP = " + str(data.WAvgSP)\
        + ", IOPV = " + str(data.IOPV)\
        + ", BondWAvgBP = " + str(data.BondWAvgBP)\
        + ", YTM = " + str(data.YTM)\
        + ", ETFBNo = " + str(data.ETFBNo)\
        + ", ETFBVOL = " + str(data.ETFBVOL)\
        + ", ETFBM = " + str(data.ETFBM)\
        + ", ETFSNo = " + str(data.ETFSNo)\
        + ", ETFSVOL = " + str(data.ETFSVOL)\
        + ", ETFSM = " + str(data.ETFSM)\
        + ", WithdrawBNo = " + str(data.WithdrawBNo)\
        + ", WithdrawBVOL = " + str(data.WithdrawBVOL)\
        + ", WithdrawBM = " + str(data.WithdrawBM)\
        + ", WithdrawSNo = " + str(data.WithdrawSNo)\
        + ", WithdrawSVOL = " + str(data.WithdrawSVOL)\
        + ", WithdrawSM = " + str(data.WithdrawSM)\
        + ", TotalBNo = " + str(data.TotalBNo)\
        + ", TotalSNo = " + str(data.TotalSNo)\
        + ", MaxBD = " + str(data.MaxBD)\
        + ", MaxSD = " + str(data.MaxSD)\
        + ", BONo = " + str(data.BONo)\
        + ", SONo = " + str(data.SONo)\
        + ", TradeStatus = " + str(data.TradeStatus)\
        + ", TradeNo = " + str(data.TradeNo)\
        + ", TradeVolume = " + str(data.TradeVolume)\
        + ", TradeAmount = " + str(data.TradeAmount)\
        + ", Status = " + str(data.Status)\
        + ", PE1 = " + str(data.PE1)\
        + ", NAV = " + str(data.NAV)\
        + ", PE2 = " + str(data.PE2)\
        + ", PremiumRate = " + str(data.PremiumRate)\
        + ", LimitUp = " + str(data.LimitUp)\
        + ", LimitDown = " + str(data.LimitDown)\
        + ", PriceUpdown1 = " + str(data.PriceUpdown1)\
        + ", PriceUpdown2 = " + str(data.PriceUpdown2)\
        + ", SymbolSource = " + str(data.SymbolSource)\
        + ", ShortName = " + str(data.ShortName)\
        + ", Vwap = " + str(data.Vwap)\
        + ", SP = " + str(data.SP)\
        + ", LSP = " + str(data.LSP)\
        + ", LastVol = " + str(data.LastVol)\
        + ", PrePosition = " + str(data.PrePosition)\
        + ", Position = " + str(data.Position)\
        + ", PrePositionChange = " + str(data.PrePositionChange)\
        + ", LifeHigh = " + str(data.LifeHigh)\
        + ", LifeLow = " + str(data.LifeLow)\
        + ", BuyOrSell = " + str(data.BuyOrSell)\
        + strBidImplyQty + strAskImplyQty + strBestBuyQty + strBestSellQty \
        + ", ConSign = " + str(data.ConSign)\
        + ", Theta = " + str(data.Theta)\
        + ", Vega = " + str(data.Vega)\
        + ", Gamma = " + str(data.Gamma)\
        + ", Rho = " + str(data.Rho)\
        + ", Delta = " + str(data.Delta)

        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S '
        localTime = time.strftime(ISOTIMEFORMAT, time.localtime())

        #print str(localTime), dictDataStr
        with open(self._ofilename_l2, 'a') as of:
            of.writelines("L2Quote: " + str(localTime) + ":" + dictDataStr + "\n")

        return

    # L1Quote行情回调函数示例
    def OnSubQuote(self, data):
        global  g_L1QuoteLeft
        g_L1QuoteLeft -= 1
        dictDataStr = ''

        strBuyPrice = ", BuyPrice = "
        for iter in data.BuyPrice:
            strBuyPrice = strBuyPrice + str(iter) + ','

        strBuyVolume = ", BuyVolume = "
        for iter in data.BuyVolume:
            strBuyVolume = strBuyVolume + str(iter) + ','

        strSellPrice = ", SellPrice = "
        for iter in data.SellPrice:
            strSellPrice = strSellPrice + str(iter) + ','

        strSellVolume = ", SellVolume = "
        for iter in data.SellVolume:
            strSellVolume = strSellVolume + str(iter) + ','

        dictDataStr = ": Symbol = " + str(data.Symbol)\
        + ", TradingDate = " + str(data.TradingDate)\
        + ", TradingTime = " + str(data.TradingTime)\
        + ", UNIX = " + str(data.UNIX)\
        + ", Market = " + str(data.Market)\
        + ", LCP = " + str(data.LCP)\
        + ", OP = " + str(data.OP)\
        + ", HIP = " + str(data.HIP)\
        + ", LOP = " + str(data.LOP)\
        + ", CP = " + str(data.CP)\
        + ", CP1 = " + str(data.CP1)\
        + ", TQ = " + str(data.TQ)\
        + ", TM = " + str(data.TM)\
        + strBuyPrice + strBuyVolume + strSellPrice + strSellVolume\
        + ", BS = " + str(data.BS)\
        + ", ChangeRatio = " + str(data.ChangeRatio)\
        + ", CQ = " + str(data.CQ)\
        + ", CM = " + str(data.CM)\
        + ", Vwap = " + str(data.Vwap)\
        + ", OrderRate = " + str(data.OrderRate)\
        + ", OrderDiff = " + str(data.OrderDiff)\
        + ", Amplitude = " + str(data.Amplitude)\
        + ", VolRate = " + str(data.VolRate)\
        + ", SellVOL = " + str(data.SellVOL)\
        + ", BuyVOL = " + str(data.BuyVOL)\
        + ", ShortName = " + str(data.ShortName)\
        + ", LSP = " + str(data.LSP)\
        + ", SP = " + str(data.SP)\
        + ", PrePosition = " + str(data.PrePosition)\
        + ", Position = " + str(data.Position)\
        + ", Change = " + str(data.Change)\
        + ", OC = " + str(data.OC)\
        + ", LocalTimeStamp = " + str(data.LocalTimeStamp)\
        + ", PositionChange = " + str(data.PositionChange)\
        + ", PrePositionChange = " + str(data.PrePositionChange)\
        + ", LimitUp = " + str(data.LimitUp)\
        + ", LimitDown = " + str(data.LimitDown)\
        + ", PreDelta = " + str(data.PreDelta)\
        + ", Delta = " + str(data.Delta)\
        + ", ConSign = " + str(data.ConSign)\
        + ", Gamma = " + str(data.Gamma)\
        + ", Rho = " + str(data.Rho)\
        + ", Theta = " + str(data.Theta)\
        + ", Vega = " + str(data.Vega)\
        + ", SettleGroupID = " + str(data.SettleGroupID)\
        + ", SettleID = " + str(data.SettleID)\
        + ", ConSignName = " + str(data.ConSignName)\
        + ", LastVol = " + str(data.LastVol)\
        + ", LifeLow = " + str(data.LifeLow)\
        + ", LifeHigh = " + str(data.LifeHigh)\
        + ", avgprice1 = " + str(data.avgprice1)\
        + ", BidImplyQty = " + str(data.BidImplyQty)\
        + ", AskImplyQty = " + str(data.AskImplyQty)\
        + ", Varieties = " + str(data.Varieties)\
        + ", DelSP = " + str(data.DelSP)\
        + ", PriceChange01 = " + str(data.PriceChange01)\
        + ", Change1 = " + str(data.Change1)\
        + ", BuyRatio = " + str(data.BuyRatio)\
        + ", SPD = " + str(data.SPD)\
        + ", RPD = " + str(data.RPD)\
        + ", Depth01 = " + str(data.Depth01)\
        + ", Depth02 = " + str(data.Depth02)\
        + ", TurnoverRate = " + str(data.TurnoverRate)\
        + ", CMV = " + str(data.CMV)\
        + ", TMV = " + str(data.TMV)\
        + ", PE = " + str(data.PE)\
        + ", PB = " + str(data.PB)\
        + ", Premium = " + str(data.Premium)\
        + ", PremiumRate = " + str(data.PremiumRate)\
        + ", StatusID = " + str(data.StatusID)\
        + ", AuctionPrice = " + str(data.AuctionPrice)\
        + ", AuctionVolume = " + str(data.AuctionVolume)\
        + ", BuyLevelNO = " + str(data.BuyLevelNO)\
        + ", SellLevelNO = " + str(data.SellLevelNO)\
        + ", SymbolSource = " + str(data.SymbolSource)\
        + ", NAV = " + str(data.NAV)\
        + ", IOPV = " + str(data.IOPV)\
        + ", SampleNo = " + str(data.SampleNo)\
        + ", TT = " + str(data.TT)\
        + ", CT = " + str(data.CT)\
        + ", PE1 = " + str(data.PE1)\
        + ", PE2 = " + str(data.PE2)

        ISOTIMEFORMAT = '%Y-%m-%d %H:%M:%S '
        localTime = time.strftime(ISOTIMEFORMAT, time.localtime())

        #print str(localTime), dictDataStr
        with open(self._ofilename_l1, 'a') as of:
            of.writelines("L1Quote: " + str(localTime) + ":" + dictDataStr + "\n")

        return

    # 行情订阅示例
    def SubDemo(self):
        # 为便于演示，此处示例不同类型类型行情单独演示；实际应用中不同标的不同类型行情可同时订阅

        # L1 Quote订阅、接收及退订示例
        if 1:
            #os.remove(self._ofilename_l1)

            # 注册L1行情回调函数，推荐在发起订阅之前注册相关行情回调方法
            RegSubQuoteCB(self.OnSubQuote)

            # 订阅的标的
            securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]

            # 订阅L1 Quote
            ret, errMsg = Subscribe(EQuoteData["k_Quote"], 0, securities, [])
            if ret == 0:
                print "[i] Subscribe L1Quote Success!"
            else:
                print "[x] Subscribe L1Quote Failed(", hex(ret), "): ", errMsg

            # 等待接收一定数量的行情
            while 0 < g_L1QuoteLeft:
                time.sleep(1)

            # 退订L1 Quote
            ret, errMsg = UnSubscribe(EQuoteData["k_Quote"], 0, securities, [])
            if ret == 0:
                print "[i] UnSubscribe L1Quote Success!"
            else:
                print "[x] UnSubscribe L1Quote Failed(", hex(ret), "): ", errMsg

        # L2 Quote订阅、接收及退订示例
        if 1:
            #os.remove(self._ofilename_l2)

            # 注册L2行情回调函数，推荐在发起订阅之前注册相关行情回调方法
            RegSubL2QuoteCB(self.OnSubL2Quote)

            # 订阅的标的
            securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]

            # 订阅L2 Quote
            ret, errMsg = Subscribe(EQuoteData["k_L2Quote"], 0, securities, [])
            if ret == 0:
                print "[i] Subscribe L2Quote Success!"
            else:
                print "[x] Subscribe L2Quote Failed(", hex(ret), "): ", errMsg

            # 等待接收一定数量的行情
            while 0 < g_L2QuoteLeft:
                time.sleep(1)

            # 退订L2 Quote
            ret, errMsg = UnSubscribe(EQuoteData["k_L2Quote"], 0, securities, [])
            if ret == 0:
                print "[i] UnSubscribe L2Quote Success!"
            else:
                print "[x] UnSubscribe L2Quote Failed(", hex(ret), "): ", errMsg

        # 分时行情订阅、接收及退订示例
        if 1:
            #os.remove(self._ofilename_sts)

            # 注册分时行情回调函数，推荐在发起订阅之前注册相关行情回调方法
            RegSubStsCB(self.OnSubSts)

            # 订阅的标的
            securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]

            # 订阅分时行情
            ret, errMsg = Subscribe(EQuoteData["k_Sts"], g_StsFreq, securities, [])
            if ret == 0:
                print "[i] Subscribe Sts Success!"
            else:
                print "[x] Subscribe Sts Failed(", hex(ret), "): ", errMsg

            # 等待接收一定数量的行情
            while 0 < g_StsLeft:
                time.sleep(1)

            # 退订分时行情
            ret, errMsg = UnSubscribe(EQuoteData["k_Sts"], g_StsFreq, securities, [])
            if ret == 0:
                print "[i] UnSubscribe Sts Success!"
            else:
                print "[x] UnSubscribe Sts Failed(", hex(ret), "): ", errMsg
        
        return

    # GetExchanges取交易所信息
    # 示例: 取中国证券市场上的全部交易所信息
    def GetExchanges(self):
        ret, errMsg, dataCols = GetExchanges("CHN")

        if ret == 0:
            print "[i] GetExchanges Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                ret = dataCols.to_csv('result\Test_GetExchanges.csv')
        else:
            print "[x] GetExchanges(", hex(ret), "): ", errMsg

    # GetTradeTypes取交易品种信息
    # 示例: 取商品期货所有交易品种的交易品种、交易所代码、品种ID、交易单位、
    #      最小变动价位、交易手续费和交割日期数据
    def GetTradeTypes(self):
        securityType = "S0107"  #商品期货
        fields = ["TradingType","Market","VarietyID","TradingUnit",\
                  "MinChangeUnit","TradingFee","DeliveryDate"]

        ret, errMsg, dataCols = GetTradeTypes(securityType, fields, "2017-06-16")
        if ret == 0:
            print "[i] GetTradeTypes Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                ret = dataCols.to_csv('Test_GetTradeTypes.csv')
        else:
            print "[x] GetTradeTypes(", hex(ret), "): ", errMsg

    # GetTradeCalendar取交易日历
    # 示例: 取上海证券交易所(股票、债券、基金、指数)2016-9-1到2016-9-18之间的日历日期、
    #      市场编码、是否开盘、品种ID以及是否夜盘交易的交易日历数据
    def GetTradeCalendar(self):
        markets = ["SSE"]
        fields = ["CalendarDate", "Market", "IsOpen", "TypeID", "TradingType", "IsNightTrading" ]

        ret, errMsg, dataCols = GetTradeCalendar(markets, "2016-9-1", "2016-9-18", fields)
        if ret == 0:
            print "[i] GetTradeCalendar Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetTradeCalendar.csv')
        else:
            print "[x] GetTradeCalendar(", hex(ret), "): ", errMsg

    # GetSnapData取行情快照
    # 示例: 取平安银行、万科A、浦发银行、中国石化的证券代码、交易所、证券简称、
    #      交易发生时间、今开盘价、卖一价、卖一量、买一价和买一量的实时行情快照数据
    def GetSnapData(self):
        securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]
        fields = ["Symbol", "Market", "ShortName", "TradingTime", "OP", "S1", "SV1", "B1", "BV1"]

        ret, errMsg, dataCols = GetSnapData(securities, [], EQuoteData["k_Quote"], fields)
        if ret == 0:
            print "[i] GetSnapData Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetSnapData.csv')
        else:
            print "[x] GetSnapData(", hex(ret), "): ", errMsg

    # GetPlates取所有板块信息
    # 示例: 取股票证监会行业类板块的所有板块信息（查当前信息）数据
    def GetPlates(self):
        includeHis = True
        securityType = ["S0101"]    #股票
        plateTypes = ["P4901"]      #证监会行业类板块

        ret, errMsg, dataCols = GetPlates(False, securityType, plateTypes)
        if ret == 0:
            print "[i] GetPlates Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetPlates.csv')
        else:
            print "[x] GetPlates(", hex(ret), "): ", errMsg

    # GetRelatedPlates取证券归属的所有板块信息
    # 示例: 取股票平安银行归属的所有板块信息数据
    def GetRelatedPlates(self):
        securities = ["000001.SZSE"]

        ret, errMsg, dataCols = GetRelatedPlates(securities)
        if ret == 0:
            print "[i] GetRelatedPlates Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv("Test_GetRelatedPlates.csv")
        else:
            print "[x] GetRelatedPlates(", hex(ret), "): ", errMsg

    # GetPlateSymbols取板块包含的证券清单信息(只支持查询叶子节点)
    # 示例: 取1006010001沪深股票板块叶子节点包含的证券清单信息(只支持查询叶子节点)数据
    def GetPlateSymbols(self):
        plateIDs = [1001001] #全部A股的代码

        ret,errorMsg,dataCols = GetPlateSymbols(plateIDs, ESetOper["k_SetUnion"])
        if ret == 0:
            print "[i] GetPlateSymbols Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('result\Test_GetPlateSymbols.csv')
        else:
            print "[x] GetPlateSymbols(", hex(ret), "): ", errMsg

    # GetSecurityInfo取提取股票、基金、债券、期货、个股期权、股指期权、指数的静态信息
    # 示例: 取股票平安银行、万科A、浦发银行和中国石化的证券代码、交易所代码、中文简称、
    #      证券上市状态编码、上市日期和发行价格的静态信息数据
    def GetSecurityInfo(self):
        securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]
        fields = ["Symbol","Market", "ShortName", "StatusID", "ListedDate", "IssuePrice"]

        ret, errMsg, dataCols = GetSecurityInfo(securities, [], fields)
        if ret == 0:
            print "[i] GetSecurityInfo Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                ret = dataCols.to_csv('Test_GetSecurityInfo.csv')
        else:
            print "[x] GetSecurityInfo(", hex(ret), "): ", errMsg

    # GetSecurityCurInfo取提取股票、基金、债券、期货、个股期权、股指期权、指数的盘前信息
    # 示例: 取平安银行、万科A、浦发银行和中国石化的证券代码、交易所代码、证券简称、总股本、
    #      前收盘价、涨停价、跌停价、每股净资产、本年每股利润的盘前信息数据
    def GetSecurityCurInfo(self):
        securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]
        fields = ["Symbol","Market", "ShortName", "TotalShare", "LCP", \
                  "LimitUp", "LimitDown", "NAPS", "EPS"]

        ret, errMsg, dataCols = GetSecurityCurInfo(securities, [], fields)
        if ret == 0:
            print "[i] GetSecurityCurInfo Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                ret = dataCols.to_csv("Test_GetSecurityCurInfo.csv")
        else:
            print "[x] GetSecurityCurInfo(", hex(ret), "): ", errMsg

    # GetDataByTime按时间取历史数据，默认数据先按日期和时间排序，再按证券代码排序
    # 示例: 取2017-02-01到2017-03-01和2017-04-01到2017-05-01两个时间段内股票
    #      平安银行、万科A、浦发银行和中国石化5分钟证券代码、交易所代码、交易时间、
    #      开盘价、最高价、最低价和收盘价的历史数据
    def GetDataByTime(self):
        securities = ["000008.SZSE", "000009.SZSE"]
        fields = ["Symbol","Market", "TradingTime", "OP", "HIP", "LOP", "CP"]
        timePeriods = [['2017-07-01 00:00:00.000', '2017-07-04 00:00:00.000']]

        ret, errMsg, dataCols = GetDataByTime(securities, [], fields, \
                                            EQuoteType["k_Minute"], 5, timePeriods)
        if ret == 0:
            print "[i] GetDataByTime Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('result\Test_GetDataByTime.csv')
        else:
            print "[x] GetDataByTime(", hex(ret), "): ", errMsg

    # GetDataByCount按数量取历史数据，默认数据先按日期和时间排序，
    # 再按证券代码排序，不保证数据按时间对齐
    # 示例: 取2017-03-24日凌晨12点前向前5分钟的100条股票平安银行、万科A、
    #      浦发银行和中国石化5分钟证券代码、交易所代码、交易时间、开盘价、
    #      最高价、最低价和收盘价的历史数据
    def GetDataByCount(self):
        securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]
        fields = ["Symbol","Market", "TradingTime", "OP", "HIP", "LOP", "CP"]

        ret, errMsg, dataCols = GetDataByCount(securities, [], fields, EQuoteType["k_Minute"],\
                                     5, "2017-03-24 00:00:00.000", EDirection["k_Forward"], 100)

        if ret == 0:
            print "[i] GetDataByCount Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetDataByCount.csv')
        else:
            print "[x] GetDataByCount(", hex(ret), "): ", errMsg

    # GetTickByTime按时间取TICK数据
    # 示例: 取郑商所白糖期权SR1809-P-7400 2017-06-19到2017-06-20时间段内证券代码、证券简称、
    #      交易时间、开盘价、最高价、最低价和收盘价的TICK数据
    def GetTickByTime(self):
        security = "SR1809-P-7400.CZCE"
        fields = ["Symbol","ShortName", "TradingTime", "OP", "HIP", "LOP", "CP"]
        timePeriods = [['2017-06-19 00:00:00.000', '2017-06-20 00:00:00.000']]

        ret, errMsg, dataCols = GetTickByTime(security, 0, fields, timePeriods)
        if ret == 0:
            print "[i] GetTickByTime Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetTickByTime.csv')
        else:
            print "[x] GetTickByTime(", hex(ret), "): ", errMsg

    # GetTickByCount按数量取TICK数据
    # 示例: 取郑商所白糖期权SR1809-P-7400 2017-06-20日凌晨12点向前100条证券代码、证券简称、
    #      交易时间、开盘价、最高价、最低价和收盘价的TICK数据
    def GetTickByCount(self):
        security = "SR1809-P-7400.CZCE"
        fields = ["Symbol","ShortName", "TradingTime", "OP", "HIP", "LOP", "CP"]

        ret, errMsg, dataCols = GetTickByCount(security, 0, fields,\
                                    "2017-06-20 00:00:00.000", EDirection["k_Forward"], 100)
        if ret == 0:
            print "[i] GetTickByCount Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetTickByCount.csv')
        else:
            print "[x] GetTickByCount(", hex(ret), "): ", errMsg

    # GetL2TickByTime按时间取Level-2数据（支持沪深股票）
    # 示例: 取深交所股票平安银行 2015-03-24到2017-03-25 时间段内证券代码、
    #      交易所代码、交易时间、开盘价、最高价、最低价和收盘价的L2TICK数据
    def GetL2TickByTime(self):
        security = "000001.SZSE"
        fields = ["Symbol","Market", "TradingTime", "OP", "HIP", "LOP", "CP"]
        timePeriods = [['2017-03-24 00:00:00.000', '2017-03-25 00:00:00.000']]

        ret, errMsg, dataCols = GetL2TickByTime(security, 0, EQuoteData["k_L2Quote"],\
                                              fields, timePeriods)
        if ret == 0:
            print "[i] GetL2TickByTime Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetL2TickByTime.csv')
        else:
            print "[x] GetL2TickByTime(", hex(ret), "): ", errMsg

    # GetL2TickByCount按数量取Level-2数据（支持沪深股票）
    # 示例: 取深交所股票平安银行 2015-03-24凌晨12点前向前取100条证券代码、交易所代码、
    #      交易时间、开盘价、最高价、最低价和收盘价的L2TICK数据
    def GetL2TickByCount(self):
        security = "000001.SZSE"
        fields = ["Symbol","Market", "TradingTime", "OP", "HIP", "LOP", "CP"]

        ret, errMsg, dataCols = GetL2TickByCount(security, 0, EQuoteData["k_L2Quote"], fields, \
                                    "2017-03-24 00:00:00.000", EDirection["k_Forward"], 100)
        if ret == 0:
            print "[i] GetL2TickByCount Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetL2TickByCount.csv')
        else:
            print "[x] GetL2TickByCount(", hex(ret), "): ", errMsg

    # GetFinance取财务因子
    # 示例: 取股票平安银行、万科A、浦发银行和中国石化2017-01-01到2017-04-01时间段内的
    #      BEPS、TOTOR、TOLPRO的财务因子数据（日频）
    def GetFinance(self):
        securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]
        fields = ["Symbol","Market", "BEPS", "TOTOR", "TOLPRO"]

        ret, errMsg, dataCols = GetFinance(securities, [], fields, "2017-01-01", "2017-04-01",\
                                EReportType["k_RptMergeCur"], ETrailType["k_TrailSeason"], \
                                ERptDateType["k_RptDateIssue"])
        if ret == 0:
            print "[i] GetFinance Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetFinance.csv')
        else:
            print "[x] GetFinance(", hex(ret), "): ", errMsg

    # GetFactor取量化及风控因子
    # 示例: 取股票平安银行、万科A、浦发银行和中国石化2017-01-01到2017-05-05时间段内的交易日期、
    #      每股净资产、市盈率的量化及风控因子（日频）
    def GetFactor(self):
        securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]
        fields = ["Symbol","Market", "TradingDate", "QF_NetAssetPS", "QF_PE"]

        ret, errMsg, dataCols = GetFactor(securities, [], fields, "2017-01-01", "2017-05-05")
        if ret == 0:
            print "[i] GetFactor Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetFactor.csv')
        else:
            print "[x] GetFactor(", hex(ret), "): ", errMsg

    # GetHisMarketInfo取证券历史变动信息（分红派息停复牌等）
    # 示例: 取股票平安银行、万科A、浦发银行和中国石化2010-10-03到2017-03-24时间段内的除权除息日、
    #      税前每股分红和送股比例的证券历史变动信息数据（分红派息停复牌等）
    def GetHisMarketInfo(self):
        securities = ["000001.SZSE", "000002.SZSE", "600000.SSE", "600028.SSE"]
        fields = ["Symbol","Market", "ExDividendDate", "DividentBT", "BonusRatio"]

        ret,errMsg,dataCols = GetHisMarketInfo(securities, [], fields,\
                                                    "2010-10-03", "2017-03-24")
        if ret == 0:
            print "[i] GetHisMarketInfo Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetHisMarketInfo.csv')
        else:
            print "[x] GetHisMarketInfo(", hex(ret), "): ", errMsg

    # GetJointContracts取期货主力连续或连续合约信息，按连续合约代码和日期排序
    # 示例: 取2017-01-01到2017-04-30时间段内豆一主力连续合约和豆一次主力合约信息
    def GetJointContracts(self):
        contracts = ["ACC01", "AM02"]

        ret, errMsg, dataCols = GetJointContracts(contracts, "2017-01-01", "2017-04-30")
        if ret == 0:
            print "[i] GetJointContracts Success! Rows = ", len(dataCols)
            if g_toScreen:
                print dataCols, '\n'
            if g_toFile:
                dataCols = ConvertStr(dataCols)
                dataCols.to_csv('Test_GetJointContracts.csv')
        else:
            print "[x] GetJointContracts(", hex(ret), "): ", errMsg            

def GetAllStockSecurityInfo():
    plateIDs = [1001001] #全部A股的代码
    ret,errorMsg,dataCols = GetPlateSymbols(plateIDs, ESetOper["k_SetUnion"])
    if ret == 0:
        print "[i] GetDataByTime Success! Rows = ", len(dataCols)
        bToScreen = False
        if bToScreen:
            print dataCols, '\n'          
        return dataCols
    else:
        print "[x] GetDataByTime(", hex(ret), "): ", errMsg    
        return -1
    
def WriteToDataBase(data, dataBaseName):
    print 'WriteTODataBase'

def TestGetAllHistData(security):
    # securitityIDS = [201000000002]
    # securitityIDS = []
    # securitityIDS.append(securityID)
    securities = [];
    securities.append(security)
    fields = ["TradingTime","TradingDate", "Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
    timePeriods = [['2017-07-01 00:00:00.000', '2017-08-01 00:00:00.000']]
    timeInterval = 5
    ret, errMsg, dataCols = GetDataByTime(securities, [], fields, \
                                        EQuoteType["k_Minute"], timeInterval, timePeriods)
    dirName = 'TmpResult\\'
    fileName = security
    completeFileName = dirName + fileName + '.csv'
    if ret == 0:
        print "[i] GetDataByTime Success! Rows = ", len(dataCols)
        if g_toScreen:
            print dataCols, '\n'
        if g_toFile:
            dataCols = ConvertStr(dataCols)
            # dataCols.to_csv('result\Test_GetDataByTime.csv')
            dataCols.to_csv(completeFileName);
    else:
        print "[x] GetDataByTime(", hex(ret), "): ", errMsg    

def GetAllSecurityTradeInfo():
    allStockSecurityInfo = GetAllStockSecurityInfo()
    # WriteToDataBase(allStockSecurityInfo, 'stock_securityId')
    
    # completeStockID = allStockSecurityInfo.iloc[0, 2] + '.' + str(allStockSecurityInfo.iloc[0, 0])

    # for i in range(0, 10):
    #     completeStockID = allStockSecurityInfo.iloc[i, 2] + '.' + str(allStockSecurityInfo.iloc[i, 0])
    #     print 'completeStockID: ', completeStockID
    #     TestGetAllHistData(completeStockID)

# 主程序
if __name__=='__main__': 

    print os.getcwd()

    #在QtAPIDemo.id填入GTA登录的用户名和密码
    bret, qt_usr, qt_pwd = GetUsrPwd(os.getcwd() + "\\QtAPIDemo.id")
    testApi = TestApi()

    # 登录GTA认证服务，初始化QtAPI运行环境
    if bret:
        ret, errMsg = QtLogin(qt_usr, qt_pwd)
        if ret == 0:
            print "[i] QtLogin Success!"
        else:
            print "[x] QtLogin Failed(", hex(ret), "): ", errMsg
    else:
        print "[x] Can't get usr/pwd"
        exit()

    testApi.GetExchanges()

    # testApi.GetTradeTypes()

    # testApi.GetTradeCalendar()

    # testApi.GetPlates()

    # testApi.GetPlateSymbols()

    # testApi.GetDataByTime()

    # 行情订阅demo
    # SubDemo()

    # GetAllSecurityTradeInfo()

    k = g_BeatInterval
    while g_cycle:
        time.sleep(1)
        k -= 1
        if 0 == k:
          print "[i] QtAPIDemo is running!"
          k = g_BeatInterval

    # 从GTA认证服务登出
    if 1:
        ret, errMsg = QtLogout(qt_usr)
        if ret == 0:
            print "[I] QtLogout Success!"
        else:
            print "[X] QtLogout Failed(", hex(ret), "): ", errMsg

    sys.exit(0)

    # endof __main__