# -*- coding: UTF-8 -*-
import time
import pickle
import string
from QtAPI import *
from QtDataAPI import *
from TestApi import TestApi
from example import MSSQL
from toolFunc import *

g_BeatInterval = 5  # 运行信号输出间隔
g_cycle    = False  # Demo程序是否持续运行

g_toScreen = False  # 提取的数据是否输出到屏幕
g_toFile   = True   # 提取的数据是否输出到文件

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

# 分时行情回调函数示例
def DemonRun():
    k = g_BeatInterval
    while g_cycle:
        time.sleep(1)
        k -= 1
        if 0 == k:
          print "[i] QtAPIDemo is running!"
          k = g_BeatInterval

def convertDatetime(oriDateStr, oriTimeStr):
    print ('oriDateStr = %s, oriTimeStr = %s') % (oriDateStr, oriTimeStr)
    dateArray = oriDateStr.split(' ')
    timeArray = oriTimeStr.split(' ')
    print dateArray
    print timeArray
    dateStr = dateArray[0].replace('-','')
    timeStr = timeArray[1].replace(':','').split('.')[0]
    print dateStr
    print timeStr
    dateInt = string.atoi(dateStr)
    timeInt = string.atoi(timeStr)
    print dateInt
    print timeInt    
    return dateStr, timeStr

def getIntDate(oriDateStr):
    dateArray = oriDateStr.split(' ')
    dateStr = dateArray[0].replace('-','')
    # dateInt = string.atoi(dateStr)
    # print dateArray
    # print dateStr
    # print dateInt
    return dateStr   

def getSimpleDate(oriDateStr):
    dateArray = oriDateStr.split(' ')
    dateStr = dateArray[0].replace('-','')
    return dateStr   

def getSimpleTime(oriTimeStr):
    timeArray = oriTimeStr.split(' ')
    timeStr = timeArray[1].replace(':','').split('.')[0]
    return timeStr   

def testConvertDatetime():
    oriDateStr = "2017-07-03 09:30:00.000"
    oriTimeStr = "2017-07-03 08:00:00.000"
    # convertDatetime(oriDateStr, oriTimeStr)
    print getIntDate(oriDateStr)
    print getIntTime(oriTimeStr)


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
        print "[x] GetDataByTime(", hex(ret), "): ", errorMsg
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

'''
功能： 测试原始数据是什么样的形式，每一个元素是什么类型，如何存取;
'''
def testDataType(data):
    print type(data)
    print len(data)
    for i in range(0, len(data.iloc[0])):
        print "len(exchangeData.iloc[0, %d]  type is %s \n"%(i, type(data.iloc[0, i]))
'''
功能： 测试ExchangeData的读取与存储;
结果： 测试成功, 可以正常读取写入到数据库;
'''
def testWriteExchangeData(oriDataObj):
    result = oriDataObj.GetExchanges()
    # testDataType(result)
    databaseObj = MSSQL()   
    desTableName = "[dbo].[AExchangeData]"
    colStr = "(CoutryCode , ENName , Market , Marketname ) "
    for i in range(0, len(result)): 
        valStr = "\'" + result.iloc[i, 0] + "\', \'" + result.iloc[i, 1] + "\', \'" \
                + result.iloc[i, 2] + "\', \'" + result.iloc[i, 3] + "\'" 

        insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
        print insertStr
        insertRst = databaseObj.ExecStoreProduce(insertStr)

'''
功能： 测试从数据源读取后写入到数据库的数据是否正确
结果： 正确；
'''
def testReadExchangeDataFromDatabase():
    databaseObj = MSSQL()   
    originDataTable = "[dbo].[AExchangeData]"
    queryString = 'select * from ' + originDataTable
    result = databaseObj.ExecQuery(queryString)
    print result
    return result

'''
功能： 测试HistData的读取与存储;
'''        
def testWriteHistByTimeData(oriDataObj):
    result = oriDataObj.GetDataByTime()    
    if type(result) == 'int':
        print 'GetDataByTime Failed!'
    else:
        starttime = datetime.datetime.now()
        print "\n++++ Start Time: %s ++++ \n" %(starttime)

        databaseObj = MSSQL() 
        desTableName = "[dbo].[ATestTable_6]"
        for i in range(0, len(result)):
            colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
            valStr = getSimpleDate(result.iloc[i, 0]) + ", " + getSimpleTime(result.iloc[i, 1]) + ", \'"+ result.iloc[i, 2] + "\'," \
                    + str(result.iloc[i, 3]) + ", " + str(result.iloc[i, 4]) + ", " + str(result.iloc[i, 5]) + ", " \
                    + str(result.iloc[i, 6]) + ", " + str(result.iloc[i, 7]) + ", " + str(result.iloc[i, 8]) + ", " \
                    + str(result.iloc[i, 9])                    

            insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
            if i < 0:
                # print 'insertStr: %s'%(insertStr)
                pass
            insertRst = databaseObj.ExecStoreProduce(insertStr)    

        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        print "\n+++++ End Time: %s ++++++" %(endtime)
        print 'DataCount: %d, Cost Time: %d%s\n' %(len(result), deletaTime.seconds, "s")
'''
功能： 测试从数据源读取后写入到数据库的数据是否正确
结果： 
'''
def testReadHistByTimeDataFromDatabase():
    databaseObj = MSSQL()   
    originDataTable = "[dbo].[ATestTable_0]"
    queryString = 'select * from ' + originDataTable
    result = databaseObj.ExecQuery(queryString)
    print result
    return result

'''
功能： 得到所有三千多支证券的总计交易数据量
'''
def getSumSecodeDataCount():
    databaseObj = MSSQL()
    originDataTable = '[dbo].[SecodeInfo]'
    queryString = 'select SECODE, EXCHANGE from ' + originDataTable
    result = databaseObj.ExecQuery(queryString)

    resultFileName = "secodeResult.txt"
    wfile = open(resultFileName, 'w')
    rstStr = "SecodeInfo numb is  : " + str(len(result)) + '\n'
    LogInfo(wfile, rstStr)

    count = 0
    secondeCount = len(result)
    for i in range(0, 1):
        
        security = result[i][0] + '.'
        if result[i][1] == 'SZ':
            security = security + 'SZSE'
        if result[i][1] == 'SH':
            security = security + 'SSE'

        securities = [];
        securities.append(str(security))
        print securities
        fields = ["TradingTime","TradingDate", "Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
        timePeriods = [['2014-02-01 00:00:00.000', '2017-9-11 00:00:00.000']]
        timeInterval = 5
        ret, errMsg, dataCols = GetDataByTime(securities, [], fields, \
                                            EQuoteType["k_Minute"], timeInterval, timePeriods)

        if ret == 0:
            rstStr = security + " : " + str(len(dataCols)) + '\n'
            LogInfo(wfile, rstStr)
 
            count = count + len(dataCols)
        else:
            wfile.write('errMsg: ' + errMsg)
            print "[x] GetDataByTime(", hex(ret), "): ", errMsg
        dataCols = None

    rstStr = "\nSum count is " + str(count) + '\n'
    LogInfo(wfile, rstStr)
    wfile.close()

def testWriteFile():
    resultFileName = ".\secodeResult.txt"
    wfile = open(resultFileName,'w')
    rstStr = "SecodeInfo numb is  : " + str(len([1,2,3]))
    wfile.write(rstStr)    

    rstStr = "\nSum count is " + str(11) + '\n'
    print rstStr
    wfile.write(rstStr)
    wfile.close()

def testMain():
    testApi = TestApi()
    testApi.QtLogin(QT_USR, QT_PWD)
    getSumSecodeDataCount()

    # testWriteHistByTimeData(testApi)

    # testWriteExchangeData(testApi)

    # testReadExchangeDataFromDatabase()

    # testApi.GetExchanges()

    # testApi.GetTradeTypes()

    # testApi.GetTradeCalendar()

    # testApi.GetPlates()

    # testApi.GetPlateSymbols()

    # testApi.GetDataByTime()

    # 行情订阅demo
    # SubDemo()

    # GetAllSecurityTradeInfo()

    testApi.QtLogout(qt_usr)

    # sys.exit(0)    

def testOther():
    # testConvertDatetime()    
    testWriteFile()

# 主程序
if __name__=='__main__':
    testMain()
    # testOther()

    # endof __main__
