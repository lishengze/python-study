# -*- coding: UTF-8 -*-
import time
import pickle
from QtAPI import *
from QtDataAPI import *
from TestApi import TestApi
from example import MSSQL

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
def DemonRun():
    k = g_BeatInterval
    while g_cycle:
        time.sleep(1)
        k -= 1
        if 0 == k:
          print "[i] QtAPIDemo is running!"
          k = g_BeatInterval

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
    testDataType(result)
    desTableName = "[dbo].[ATestTable_0]"
    for i in range(0, len(result)):
        colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        valStr = str(result.iloc[i, 0]) + ", " + str(result.iloc[i, 1]) + ", \'"+ result.iloc[i, 2] + "\'" \
                + str(result.iloc[i, 3]) + ", " + str(result.iloc[i, 4]) + ", " + str(result.iloc[i, 5]) + ", " \
                + str(result.iloc[i, 6]) + ", " + str(result.iloc[i, 7]) + ", " + str(result.iloc[i, 8]) + ", " \
                + str(result.iloc[i, 9]) + ", " + str(result.iloc[i, 10])

        insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
        if i == 0:
            print 'insertStr: %s'%(insertStr)
        # insertRst = databaseObj.ExecStoreProduce(insertStr)    
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

# 主程序
if __name__=='__main__':
    qt_usr = "xgzc_api"
    qt_pwd = "UXLAS4YF"

    testApi = TestApi()

    testApi.QtLogin(qt_usr, qt_pwd)

    # testWriteExchangeData(testApi)

    testReadExchangeDataFromDatabase()

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

    sys.exit(0)

    # endof __main__
