# -*- coding:UTF-8 -*-
import pandas as pd
import numpy as np
import time
import datetime

import QtPyAPI

#数据类型，用于指定列式数据的类型及解析，与ProtoBuf协议无关
EDataType = {"k_Char":QtPyAPI.EDataType.k_Char,
            "k_Bool":QtPyAPI.EDataType.k_Bool,
            "k_Byte":QtPyAPI.EDataType.k_Byte,
            "k_Int8":QtPyAPI.EDataType.k_Int8,
            "k_UInt8":QtPyAPI.EDataType.k_UInt8,
            "k_Int16":QtPyAPI.EDataType.k_Int16,
            "k_UInt16":QtPyAPI.EDataType.k_UInt16,
            "k_Int32":QtPyAPI.EDataType.k_Int32,
            "k_UInt32":QtPyAPI.EDataType.k_UInt32,
            "k_Int64":QtPyAPI.EDataType.k_Int64,
            "k_UInt64":QtPyAPI.EDataType.k_UInt64,
            "k_Float":QtPyAPI.EDataType.k_Float,
            "k_Double":QtPyAPI.EDataType.k_Double,
            "k_DateTime":QtPyAPI.EDataType.k_DateTime,#实质为以uint64表示的毫秒数，若库中数据时间信息实质为字符串型，一律转为本类型。分时数据
            "k_TimeStamp":QtPyAPI.EDataType.k_TimeStamp#实质为以uint64表示的微秒数，若库中数据时间信息实质为字符串型，一律转为本类型。tick信息
            }

EQtBool = {"k_QtFalse":QtPyAPI.EQtBool.k_QtFalse,
            "k_QtTrue":QtPyAPI.EQtBool.k_QtTrue,      
            "k_QtNull":QtPyAPI.EQtBool.k_QtNull
            }

#集合操作，用于数据结果集之间的集合操作，暂只考虑并、交两种
ESetOper = {"k_SetUnion":QtPyAPI.ESetOper.k_SetUnion,#并集
            "k_SetInter":QtPyAPI.ESetOper.k_SetInter#交集     
           # "k_SetComp":QtPyAPI.ESetOper.k_SetComp#补集 
            }

#排序类型，用于指定数据结果集的排序要求
ESortType = {"k_SortNone":QtPyAPI.ESortType.k_SortNone,#不排序
            "k_SortDesc":QtPyAPI.ESortType.k_SortDesc,#降序     
            "k_SortAsec":QtPyAPI.ESortType.k_SortAsec#升序
             }

#用于指明数据提取的方向
EDirection = {"k_Forward":QtPyAPI.EDirection.k_Forward,#向前，时间点以前
             "k_Backward":QtPyAPI.EDirection.k_Backward#向后，时间点以后
              }

#行情采样类型
EQuoteType = {"k_Second":QtPyAPI.EQuoteType.k_Second,#秒，日内高频
              "k_Minute":QtPyAPI.EQuoteType.k_Minute,#分，日内高频    
              "k_Hour":QtPyAPI.EQuoteType.k_Hour,#时，日内高频 
              "k_Day":QtPyAPI.EQuoteType.k_Day,#日，低频
              "k_Week":QtPyAPI.EQuoteType.k_Week,#周，低频
              "k_Month":QtPyAPI.EQuoteType.k_Month,#月，低频
              "k_Quarter":QtPyAPI.EQuoteType.k_Quarter,#季，低频
              "k_Year":QtPyAPI.EQuoteType.k_Year#年，低频
              }

#报告类型，主要用于财务因子/报表数据
EReportType = {"k_RptMergeCur":QtPyAPI.EReportType.k_RptMergeCur,#合并本期
               "k_RptMergePre":QtPyAPI.EReportType.k_RptMergePre,#合并上期
               "k_RptParentCur":QtPyAPI.EReportType.k_RptParentCur,#母公司本期
               "k_RptParentPre":QtPyAPI.EReportType.k_RptParentPre#母公司上期
              }

#报告日期类型，主要用于财务因子/报表数据
ERptDateType = {"k_RptDateIssue":QtPyAPI.ERptDateType.k_RptDateIssue,#报告发布日期
                "k_RptDateClose":QtPyAPI.ERptDateType.k_RptDateClose#报告财期截止日期
                }

#价格复权调整类型
EPriceAdjust = {"k_AdjNone":QtPyAPI.EPriceAdjust.k_AdjNone,#不复权，依20160902评审建议增加
                "k_AdjForward":QtPyAPI.EPriceAdjust.k_AdjForward,#前复权
                "k_AdjBackward":QtPyAPI.EPriceAdjust.k_AdjBackward#后复权
                }

#财务报表累计类型
ETrailType = {"k_TrailSeason":QtPyAPI.ETrailType.k_TrailSeason,#单季度
                "k_TrailAddup":QtPyAPI.ETrailType.k_TrailAddup,#季度累计
                "k_Trail12Mon":QtPyAPI.ETrailType.k_Trail12Mon#TTM，12个月滚动累计
              }

#行情数据类型
EQuoteData = {"k_QuoteNone":QtPyAPI.EQuoteData.k_QuoteNone,
              "k_Quote":QtPyAPI.EQuoteData.k_Quote,#行情类消息，沪深L1、中金所L2、商品期货L1、上海L1个股期权
              "k_Sts":QtPyAPI.EQuoteData.k_Sts,#分时消息，沪深L1、中金所L2、商品期货L1、上海L1个股期权
              "k_Arbitrage":QtPyAPI.EQuoteData.k_Arbitrage,#L1套利行情(大商所)
              "k_Static":QtPyAPI.EQuoteData.k_Static,#静态数据(上海L2、深圳L2、上交所个股期权)
              "k_Bulletin":QtPyAPI.EQuoteData.k_Bulletin,#公告及增值信息(深圳L1)
              "k_L2Auction":QtPyAPI.EQuoteData.k_L2Auction,#L2集合竞价(上海)
              "k_L2Index":QtPyAPI.EQuoteData.k_L2Index,#L2指数行情(上海、深圳)
              "k_L2Order":QtPyAPI.EQuoteData.k_L2Order,#L2逐笔委托(深圳)
              "k_L2Orderqueue":QtPyAPI.EQuoteData.k_L2Orderqueue,#L2委托队列(上海、深圳)
              "k_L2Quote":QtPyAPI.EQuoteData.k_L2Quote,#L2十档行情(上海、深圳)
              "k_L2Transaction":QtPyAPI.EQuoteData.k_L2Transaction,#L2逐笔成交(上海、深圳)
              "k_L2Status":QtPyAPI.EQuoteData.k_L2Status,#L2证券状态(深圳)

              "k_L2Arbitrage":QtPyAPI.EQuoteData.k_L2Arbitrage,#L2套利行情
              "k_L2MarchPriceQty":QtPyAPI.EQuoteData.k_L2MarchPriceQty,#L2分价成交量行情
              "k_L2OrderStatistic":QtPyAPI.EQuoteData.k_L2OrderStatistic,#L2委托统计行情
              "k_L2RealTimePrice":QtPyAPI.EQuoteData.k_L2RealTimePrice#L2实时结算价
             }

def GetDoubleSeq():
    QtPyAPI.DoubleSeq();

def CallOnSubl2Order(num):
    QtPyAPI.CallOnSubl2Order(num);

# @brief 注册实时分时数据回调方法
# @param obj 接收数据函数对象
def RegSubStsCB(cbFunction):
    return QtPyAPI.SetSubStsCB(cbFunction)

# @brief 注册实时Tick数据回调方法
# @param obj 接收数据函数对象
def RegSubQuoteCB(cbFunction):
    return QtPyAPI.SetSubQuoteCB(cbFunction)

# @brief 注册实时L2十档行情(上海、深圳)
# @param obj 接收数据函数对象
def RegSubL2QuoteCB(cbFunction):
    return QtPyAPI.SetSubL2QuoteCB(cbFunction)

# @brief 注册L1套利行情(大商所)
# @param obj 接收数据函数对象
def RegSubArbitrageCB(cbFunction):
    return QtPyAPI.SetSubArbitrageCB(cbFunction)

# @brief 注册静态数据(上海L2、深圳L2、上交所个股期权)
# @param obj 接收数据函数对象
def RegSubStaticCB(cbFunction):
    return QtPyAPI.SetSubStaticCB(cbFunction)

# @brief 注册公告及增值信息(深圳L1)
# @param obj 接收数据函数对象
def RegSubBulletinCB(cbFunction):
    return QtPyAPI.SetSubBulletinCB(cbFunction)

# @brief 注册L2集合竞价(上海)
# @param obj 接收数据函数对象
def RegSubL2AuctionCB(cbFunction):
    return QtPyAPI.SetSubL2AuctionCB(cbFunction)

# @brief 注册L2指数行情(上海、深圳)
# @param obj 接收数据函数对象
def RegSubL2IndexCB(cbFunction):
    return QtPyAPI.SetSubL2IndexCB(cbFunction)

# @brief 注册L2逐笔委托(深圳)
# @param obj 接收数据函数对象
def RegSubL2OrderCB(cbFunction):
    return QtPyAPI.SetSubL2OrderCB(cbFunction)

# @brief 注册L2委托队列(上海、深圳)
# @param obj 接收数据函数对象
def RegSubL2OrderQueueCB(cbFunction):
    return QtPyAPI.SetSubL2OrderQueueCB(cbFunction)

# @brief 注册L2逐笔成交(上海、深圳)
# @param obj 接收数据函数对象
def RegSubL2TransactionCB(cbFunction):
    return QtPyAPI.SetSubL2TransactionCB(cbFunction)

# @brief 注册L2证券状态(深圳)
# @param obj 接收数据函数对象
def RegSubL2StatusCB(cbFunction):
    return QtPyAPI.SetSubL2StatusCB(cbFunction)

# @brief 注册L2套利行情
# @param obj 接收数据函数对象
def RegSubL2ArbitrageCB(cbFunction):
    return QtPyAPI.SetSubL2ArbitrageCB(cbFunction)

# @brief 注册L2分价成交量行情
# @param obj 接收数据函数对象
def RegSubL2MarchPriceQtyCB(cbFunction):
    return QtPyAPI.SetSubL2MarchPriceQtyCB(cbFunction)

# @brief 注册L2委托统计行情
# @param obj 接收数据函数对象
def RegSubL2OrderStatisticCB(cbFunction):
    return QtPyAPI.SetSubL2OrderStatisticCB(cbFunction)

# @brief 注册L2实时结算价
# @param obj 接收数据函数对象
def RegSubL2SettlePriceCB(cbFunction):
    QtPyAPI.SetSubL2SettlePriceCB(cbFunction)

# @brief 按symbol.market订阅行情
# @param quoteData 订阅行情类型
# @param freq 订阅数据的频率，单位秒，0为实时行情
# @param securities 订阅标的
# @param fields 订阅字段，暂未使用
# @param asPossible 尽最大可能完成订阅
def Subscribe(quoteData, freq, securities, fields, asPossible = True):
    errorMsg = QtPyAPI.string();
    securitiesTmp = QtPyAPI.StringSeq();
    fieldsTmp = QtPyAPI.StringSeq();
    securitiesTmp.extend(securities);
    fieldsTmp.extend(fields);
    ret = QtPyAPI.SubscribeForPy(errorMsg, quoteData, freq, securitiesTmp, fieldsTmp, asPossible);
    return ret, errorMsg.c_str()

# @brief 按symbol.market退订行情
# @param quoteData 订阅行情类型
# @param freq 订阅数据的频率，单位秒，0为实时行情
# @param securities 订阅标的
# @param fields 订阅字段，暂未使用
# @param asPossible 尽最大可能完成退订
def UnSubscribe(quoteData, freq, securities, fields, asPossible = True):
    errorMsg = QtPyAPI.string();
    securitiesTmp = QtPyAPI.StringSeq();
    fieldsTmp = QtPyAPI.StringSeq();
    securitiesTmp.extend(securities);
    fieldsTmp.extend(fields);
    ret = QtPyAPI.UnSubscribeForPy(errorMsg, quoteData, freq, securitiesTmp, fieldsTmp, asPossible);
    return ret, errorMsg.c_str()

# @brief 取证券归属的所有板块信息
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities 字符型证券标的列表，支持多证券同时查询
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param date 日期，若未指定则为当前日期
# @param timezone 参数中时间参数的时区，默认为东8区
# @param reserve 预留，默认为空
def GetRelatedPlates(securities, securityIDS = [], date = "", timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    colsSet = QtPyAPI.ColumnSetSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);

    ret = QtPyAPI.GetRelatedPlatesForPy(colsSet, errorMsg, securitiesTmp, securityIDSTmp, date, timezone, reserve);
    colsList = QtPyAPI.PraseColumnSetSeq(colsSet);
    colsDict = {};
    for iter in colsList:
        tmpDict = iter;
        if len(colsDict) == 0:
            colsDict = tmpDict;
            continue;
        for j in tmpDict:
            colsDict[j].extend(tmpDict[j]);

    colsDf = pd.DataFrame(colsDict);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取交易日历
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param exchangeCode 交易所标准代码
# @param dateBegin 查询起始时间[dateBegin, endDate]
# @param dateEnd 截止查询时间，YYYY-MM-DD
# @param timezone 参数中时间参数的时区，默认为东8区
# @param fields 数据字段，一个"*"表示提取全部字段
# @param securityType 证券品种代码，源于ReqSecurityTypes，不配置表示无该参数限制
# @param tradingType 交易品种代码，源于ReqTradingTypes，不配置表示无该参数限制
# @param open 开市/休市，默认为true
# @param dayOfWeek 0~6，表示周日～周六，允许多项输入（每字节一项），不配置时认为无该参数限制
# @param reserve 预留，默认为空
def GetTradeCalendar(exchangeCode, dateBegin, dateEnd, fields, dayOfWeek = [], tradeType = [], open = EQtBool["k_QtNull"], timezone = 8, securityType = "", reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    fieldsTmp = QtPyAPI.StringSeq();
    exchangeCodeTmp = QtPyAPI.StringSeq();
    dayOfWeekTmp = QtPyAPI.bytes();
    tradeTypeTmp = QtPyAPI.StringSeq();

    fieldsTmp.extend(fields);
    exchangeCodeTmp.extend(exchangeCode);
    dayOfWeekTmp.extend(dayOfWeek);
    tradeTypeTmp.extend(tradeType);

    ret = QtPyAPI.GetTradeCalendarForPy(cols, errorMsg, exchangeCodeTmp, dateBegin, dateEnd, fieldsTmp, dayOfWeekTmp, tradeTypeTmp, open, timezone, securityType, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf

# @brief 取所有板块信息
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param includeHis是否包含历史板块定义信息，默认为false查当前信息
# @param securityType 证券类型，源于ReqSecurityTypes结果的S01类中，不配置表示全部
# @param plateType 板块类型，源于ReqSecurityTypes结果的P49类中，不配置表示全部
# @param plateTreeID 根板块
# @param nodeLevel 板块级别
# @param reserve 预留，默认为空
def GetPlates(includeHis = False, securityType = [], plateType = [], nodeLevel = [], plateTreeID = "", reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();

    securityTypeTmp = QtPyAPI.StringSeq();
    plateTypeTmp = QtPyAPI.StringSeq();
    nodeLevelTmp = QtPyAPI.StringSeq();

    securityTypeTmp.extend(securityType);
    plateTypeTmp.extend(plateType);
    nodeLevelTmp.extend(nodeLevel);

    ret = QtPyAPI.GetPlatesForPy(cols, errorMsg, includeHis, securityTypeTmp, plateTypeTmp, nodeLevelTmp, plateTreeID, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    colsDf = pd.DataFrame(colsDict);
    return ret, errorMsg.c_str(), colsDf

# @brief 取所有交易品种信息
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securityType 证券品种类型，源于ReqSecurityTypes
# @param fields 数据字段，一个"*"表示提取全部字段
# @param date 日期
# @param timezone 时区
# @param reserve 预留，默认为空
def GetTradeTypes(securityType, fields, date = "", timezone = 8, reserve = ""):
 
    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();

    fieldsTmp = QtPyAPI.StringSeq();
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetTradeTypesForPy(cols, errorMsg, securityType, fieldsTmp, date, timezone, reserve);

    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf

# @brief 取全部股票、期货等交易所信息列表 
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param countryCode 国家标准代码
# @param reserve 预留，默认为空
def GetExchanges(countryCode = "", reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();

    ret = QtPyAPI.GetExchangesForPy(cols, errorMsg, countryCode, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    colsDf = pd.DataFrame(colsDict);
    return ret, errorMsg.c_str(), colsDf

# @brief 取期货主力连续或连续合约信息，按连续合约代码和日期排序
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @brief contracts 主力连续或连续合约代码，按:交易品种+M+01/02,交易品种+CC+01~04
# @brief dateBegin 起始日期，YYYY-MM_DD，[begin, end]
# @brief dateEnd 截止日期，YYYY-MM_DD
# @brief timezone 参数中时间参数的时区，默认为东8区
# @param reserve 预留，默认为空
def GetJointContracts(contracts, dateBegin, dateEnd, timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    contractsTmp = QtPyAPI.StringSeq();

    contractsTmp.extend(contracts);

    ret = QtPyAPI.GetJointContractsForPy(cols, errorMsg, contractsTmp, dateBegin, dateEnd, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    colsDf = pd.DataFrame(colsDict);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取证券历史变动信息（分红派息停复牌等）
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities 证券代码，"代码.交易所"的格式输入，对于不存在交易所的证券代码，
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，本接口不支持一个“*”提取全部可能字段
# @param dateBegin 起始日期，YYYY-MM_DD，[begin, end]
# @param dateEnd 截止日期，YYYY-MM_DD
# @param timezone 参数中时间参数的时区，不配置时表示当地时区
# @param sortDefs 排序要求
# @param reserve 预留，默认为空
def GetHisMarketInfo(securities, securityIDS, fields, dateBegin, dateEnd, sortDefs = [], timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetHisMarketInfoForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, fieldsTmp, dateBegin, dateEnd, sortDefs, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取量化及风控因子
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities 证券代码，"代码.交易所"的格式输入，对于不存在交易所的证券代码，
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，本接口不支持一个“*”提取全部可能字段
# @param dateBegin 起始日期，YYYY-MM_DD，[begin, end]
# @param dateEnd 截止日期，YYYY-MM_DD
# @param timezone 参数中时间参数的时区，不配置时表示当地时区
# @param sortDefs 排序要求
# @param reserve 预留，默认为空
def GetFactor(securities, securityIDS, fields, dateBegin, dateEnd, sortDefs = [], timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetFactorForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, fieldsTmp, dateBegin, dateEnd, sortDefs, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取财务因子
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities 证券代码，"代码.交易所"的格式输入，对于不存在交易所的证券代码，
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，本接口不支持默认一个“*”提取全部可能字段
# @param dateBegin 起始报告日期，YYYY-MM_DD，[begin, end]
# @param dateEnd 截止报告日期，YYYY-MM_DD
# @param reportType 报表类型
# @param trailType 报表累计类型
# @param timezone 参数中时间参数的时区，默认为东8区
# @param dateType 报告日期类型
# @param sortDefs 排序要求
# @param reserve 预留，默认为空
def GetFinance(securities, securityIDS, fields, dateBegin, dateEnd, rptType, trailType, dateType, sortDefs = [], timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetFinanceForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, fieldsTmp, dateBegin, dateEnd, rptType, trailType, dateType, sortDefs, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取快照数据
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities证券代码，"代码.交易所"的格式输入，对于不存在交易所的证券代码，
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，一个"*"表示提取全部字段
# @param sortDefs 排序要求
# @param reserve 预留，默认为空
def GetSnapData(securities, securityIDS, quoteData, fields, sortDefs = [], reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetSnapDataForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, quoteData, fieldsTmp, sortDefs, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 按时间取TICK数据
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param security 只支持单代码
# @param securityID 数字型证券标的，与securitiy二者只用其一
# @param fields 数据字段，一个"*"表示提取全部字段
# @param timePeriods 时间段[begin, end]，支持多时间段合并取值
# @param timezone 参数中时间参数的时区，不配置时表示当地时区
# @param reserve 预留，默认为空
def GetTickByTime(security, securityID, fields, timePeriods, timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetTickByTimeForPy(cols, errorMsg, security, securityID, fieldsTmp, timePeriods, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取提取股票、基金、债券、期货、个股期权、股指期权、指数的盘前信息
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities 证券代码
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，一个"*"表示提取全部字段
# @param sortDefs 排序要求
# @param dataBegin 起始日期，为空则为当前日期[begin, end]
# @param dateEnd 截止日期，为空则为当前日期
# @param timezone 参数中时间参数的时区，默认为东8区
# @param reserve 预留，默认为空
def GetSecurityCurInfo(securities, securityIDS, fields, sortDefs = [], dateBegin = "", dateEnd = "", timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetSecurityCurInfoForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, fieldsTmp, sortDefs, dateBegin, dateEnd, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取提取股票、基金、债券、期货、个股期权、股指期权、指数的静态信息
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities 证券代码
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，一个"*"表示提取全部字段
# @param sortDefs 排序要求
# @param updateTime 查询更新记录起始时间（不含该时刻）
# @param reserve 预留，默认为空
def GetSecurityInfo(securities, securityIDS, fields, sortDefs = [], updateTime = "", reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetSecurityInfoForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, fieldsTmp, sortDefs, updateTime, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 取板块包含的证券清单信息(只支持查询叶子节点)
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param plateIDs 板块列表，支持多板块，源于ReqPlates
# @param setOper 结果的集合处理方式，若并集或交集
# @param dataBegin 起始日期，不配置表示当前最新。[begin, end]
# @param dateEnd 截止日期，不配置表示当前最新
# @param timezone 参数中时间参数的时区，默认为东8区
# @param sortDefs 排序要求
# @param reserve 预留，默认为空
def GetPlateSymbols(plateIDs, setOper, sortDefs = [], dateBegin = "", dateEnd = "", timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    plateIDsTmp = QtPyAPI.SecurityIDSeq();

    plateIDsTmp.extend(plateIDs);

    ret = QtPyAPI.GetPlateSymbolsForPy(cols, errorMsg, plateIDsTmp, setOper, sortDefs, dateBegin, dateEnd, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    colsDf = pd.DataFrame(colsDict);
    return ret, errorMsg.c_str(), colsDf,

# @brief 按数量取TICK数据
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param security 只支持单代码
# @param securityID 数字型证券标的，与security二者只用其一
# @param fields 数据字段，一个"*"表示提取全部字段
# @param datetime 基准日期及时间YYYY-MM-DD HH:MM:SS，含本时刻数据
# @param dir 方向
# @param count 要求的数据数量
# @param timezone 参数中时间参数的时区，默认为东8区
# @param reserve 预留，默认为空
def GetTickByCount(security, securityID, fields, datetime, dir, count, timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetTickByCountForPy(cols, errorMsg, security, securityID, fieldsTmp, datetime, dir, count, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 按数量取历史数据，默认数据先按日期和时间排序，再按证券代码排序，不保证数据按时间对齐
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities  证券代码，"代码.交易所"的格式输入，对于不存在交易所的证券代码，
# @param securityIDs  数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，一个"*"表示提取全部字段
# @param quoteType 行情采样类型
# @param interval 采样间隔数值，单位按quoteType确定
# @param datetime 基准日期及时间YYYY-MM-DD HH:MM:SS，不含本时刻数据
# @param dir 方向
# @param count 要求的数据数量
# @param timezone 参数中时间参数的时区，默认为东8区
# @param sortDefs 排序要求
# @param reserve 预留，默认为空
def GetDataByCount(securities, securityIDS, fields, quoteType, interval, datetime, dir, count, sortDefs = [], timezone = 8, priceAdj = EPriceAdjust["k_AdjNone"], reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetDataByCountForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, fieldsTmp, quoteType, interval, datetime, dir, count, sortDefs, timezone, priceAdj, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief 按时间取历史数据，默认数据先按日期和时间排序，再按证券代码排序
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param securities 证券代码
# @param securityIDs 数字型证券标的列表，支持多证券同时查询，与securities二者只用其一
# @param fields 数据字段，一个"*"表示提取全部字段
# @param quoteType 行情采样类型()
# @param interval 采样间隔数值，单位按quatePeriod确定
# @param timePeriods 时间段[begin, end]，支持多时间段合并取值
# @param timezone 参数中时间参数的时区，默认为东8区
# @param priceAdj 复权类型，行情展示需要
# @param sortDefs 排序要求
# @param reserve 预留，默认为空
def GetDataByTime(securities, securityIDS, fields, quoteType, interval, timePeriods, sortDefs = [], timezone = 8, priceAdj = EPriceAdjust["k_AdjNone"], reserve = ""):
    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    securitiesTmp = QtPyAPI.StringSeq();
    securityIDSTmp = QtPyAPI.SecurityIDSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    securitiesTmp.extend(securities);
    securityIDSTmp.extend(securityIDS);
    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetDataByTimeForPy(cols, errorMsg, securitiesTmp, securityIDSTmp, fieldsTmp, quoteType, interval, timePeriods, sortDefs, timezone, priceAdj, reserve)
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf

# @brief按时间取Level-2数据（支持沪深股票）
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param security 证券代码,只支持单代码
# @param securityID 数字型证券标的列表，与security二者只用其一
# @param quoteData 行情数据类型，k_QuoteNull表示支持所有数据
# @param fields 数据字段，一个"*"表示提取数据类中的全部字段，如需提取指定字段，需输入相应的字段英文全名（需准确输入），支持多字段同时提取
# @param timePeriods 时间段[begin, end]，支持多时间段合并取值
# @param timezone 参数中时间参数的时区，默认为东8区
# @param reserve 预留，默认为空
def GetL2TickByTime(security, securityID, quoteData, fields, timePeriods, timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetL2TickByTimeForPy(cols, errorMsg, security, securityID, quoteData, fieldsTmp, timePeriods, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,

# @brief按数量取Level-2数据（支持沪深股票）
# @param cols 列式结果集
# @param errorMsg 调用失败时返回错误描述信息
# @param security 证券代码，只支持单代码
# @param securityID 数字型证券标的列表，与security二者只用其一
# @param quoteData 行情数据类型，k_QuoteNull表示支持所有数据
# @param fields 数据字段，一个"*"表示提取数据类中的全部字段，如需提取指定字段，需输入相应的字段英文全名（需准确输入），支持多字段同时提取
# @param datetime 基准日期及时间YYYY-MM-DD HH:MM:SS，不含本时刻数据
# @param dir 方向
# @param count 要求的数据数量
# @param timezone 参数中时间参数的时区，默认为东8区
# @param reserve 预留，默认为空
def GetL2TickByCount(security, securityID, quoteData, fields, datetime, dir, count, timezone = 8, reserve = ""):

    errorMsg = QtPyAPI.string();
    cols = QtPyAPI.ColumnSeq();
    fieldsTmp = QtPyAPI.StringSeq();

    fieldsTmp.extend(fields);

    ret = QtPyAPI.GetL2TickByCountForPy(cols, errorMsg, security, securityID, quoteData, fieldsTmp, datetime, dir, count, timezone, reserve);
    colsDict = QtPyAPI.PraseColumnSeq(cols);
    if fields == ["*"]:
        colsDf = pd.DataFrame(colsDict);
    else:
        removeDupFields = list(set(fields));
        removeDupFields.sort(key = fields.index);
        colsDf = pd.DataFrame(colsDict,columns=removeDupFields);
    return ret, errorMsg.c_str(), colsDf,
