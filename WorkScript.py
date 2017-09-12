# -*- coding: UTF-8 -*-
import time
import pickle
from QtAPI import *
from QtDataAPI import *
from example import MSSQL
from TestApi import TestApi
from toolFunc import getSimpleDate, getSimpleTime

from multiprocessing import cpu_count
import datetime
import threading

g_toScreen = False  # 提取的数据是否输出到屏幕
g_toFile   = True   # 提取的数据是否输出到文件
g_toGBK    = False  # 提取的数据是否进行汉字编码转换

g_DatabaseObj = MSSQL();

g_writeLogLock = threading.Lock()
g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')

def recordInfo(infoStr):
    g_logFile.write(infoStr + '\n')
    print infoStr

def recordInfoWithLock(infoStr):    
    g_writeLogLock.acquire()
    print infoStr
    g_logFile.write(infoStr + '\n')
    g_writeLogLock.release()        

'''
功能：将数据写入数据库
'''
def WriteToDataBase(databaseObj, desTableName, result):

    for i in range(0, len(result)):
        colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        valStr = getSimpleDate(result.iloc[i, 0]) + ", " + getSimpleTime(result.iloc[i, 1]) + ", \'"+ result.iloc[i, 2] + "\'," \
                + str(result.iloc[i, 3]) + ", " + str(result.iloc[i, 4]) + ", " + str(result.iloc[i, 5]) + ", " \
                + str(result.iloc[i, 6]) + ", " + str(result.iloc[i, 7]) + ", " + str(result.iloc[i, 8]) + ", " \
                + str(result.iloc[i, 9])   

        insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
        # print 'insertStr: %s'%(insertStr)
        insertRst = databaseObj.ExecStoreProduce(insertStr)

def GetSecodeInfo():
    originDataTable = '[dbo].[SecodeInfo]'
    queryString = 'select SECODE, EXCHANGE from ' + originDataTable
    result = g_DatabaseObj.ExecQuery(queryString)
    return result

def testThreadTransData(info):
    print 'testThreadTransData'
    print type(info)
    print len(info)
    print len(info[0])
    print type(info[0])
    print info[0][1]
    print info[0][0]

'''
作用： 从数据源读取每个证券的历史数据并写入数据库
过程：1. 为每个线程申请一个读取数据库的类对象
     2. 循环遍历证券代码表，组合得到每只证券的代码和交易所代码，向数据源申请历史数据 
        --- 向数据源申请数据可能是线程独立的，需要用锁控制，防止并发访问造成错误
     3. 将获得数据写入数据库表中。
'''
def InsertData(secodeInfo):
    # databaseObj = MSSQL()    
    secodeInfo = secodeInfo[0]
    for i in range(0, len(secodeInfo)):
        
        security = secodeInfo[i][0] + '.'
        if secodeInfo[i][1] == 'SZ':
            security = security + 'SZSE'
        if secodeInfo[i][1] == 'SH':
            security = security + 'SSE'
        security = str(security)

        securities = [];
        securities.append(security)
        fields = ["TradingDate", "TradingTime","Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
        timePeriods = [['2017-07-01 00:00:00.000', '2017-08-01 00:00:00.000']]
        timeInterval = 5

        ret, errMsg, dataCols = GetDataByTime(securities, [], fields, EQuoteType["k_Minute"], timeInterval, timePeriods)

        if ret == 0:
            infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " + security +" GetDataByTime Success! InfoCount = " + str(len(dataCols))
            recordInfoWithLock(infoStr)
            desTableName = '[dbo].LCY_STK_01MS_' + secodeInfo[i][1] +'_' + secodeInfo[i][0]
            # WriteToDataBase(databaseObj, desTableName, dataCols)
        else:
            infoStr = "[x] threadName: " + str(threading.currentThread().getName()) + "  " + security + " GetDataByTime Failed: " +  errMsg  
            recordInfoWithLock(infoStr)
'''
功能： 单线程获取所有历史数据并插入到数据库中
'''
def GetHistDataSingleThread():
    secodeInfo = GetSecodeInfo()
    databaseObj = MSSQL()

    for i in range(0, len(secodeInfo)):
        security = secodeInfo[i][0] + '.' + secodeInfo[i][1]
        securities = [];
        securities.append(security)
        fields = ["TradingTime","TradingDate", "Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
        timePeriods = [['2017-07-01 00:00:00.000', '2017-08-01 00:00:00.000']]
        timeInterval = 5
        ret, errMsg, dataCols = GetDataByTime(securities, [], fields, \
                                            EQuoteType["k_Minute"], timeInterval, timePeriods)

        if ret == 0:
            print "[i] GetDataByTime Success! Rows = ", len(dataCols)
            desTableName = '[dbo].LCY_STK_01MS_' + secodeInfo[i][1] +'_' + secodeInfo[i][0]
            WriteToDataBase(databaseObj, desTableName, dataCols)

        else:
            print "[x] GetDataByTime(", hex(ret), "): ", errMsg    

'''
作用：获取所有证券的历史数据
过程：1. 从数据库获取证券的代码信息。
     2. 根据CPU的数目和证券数设置读写线程的个数。
     3. 将证券代码信息按照线程数均分给不同的线程。
'''
def GetHistDataMultiThread():
    secodeInfo = GetSecodeInfo()
    threadCount = 3
    numbInterval = len(secodeInfo) / threadCount
    
    if len(secodeInfo) % threadCount != 0:
        threadCount = threadCount + 1

    infoStr = 'secodeInfo count:' + str(len(secodeInfo)) + ', numbInterval: ' + str(numbInterval) + ', threadCount:' + str(threadCount)
    recordInfo(infoStr)

    threads = []
    for i in range(0, threadCount):
        startIndex = i * numbInterval
        endIndex = min((i+1) * numbInterval, len(secodeInfo))
        # print (startIndex, endIndex)
        threadSecodeInfo = secodeInfo[startIndex:endIndex]
        tmp = threading.Thread(target = InsertData, args = ([threadSecodeInfo],))
        threads.append(tmp)

    starttime = datetime.datetime.now()
    infoStr = "+++++++++ Start Time: " + str(starttime) + " +++++++++++"
    recordInfo(infoStr)

    for thread in threads:
        thread.setDaemon(True)
        thread.start()
    thread.join()

    endtime = datetime.datetime.now()
    deletaTime = endtime - starttime

    infoStr = "++++++++++ End Time: " + str(endtime) +  ' Multi Thread Running Time: ' + str(deletaTime.seconds)  + "s ++++++++"    
    recordInfo(infoStr)

def main():
    qt_usr = "xgzc_api"
    qt_pwd = "UXLAS4YF"
    print "username: %s, password: %s" %(qt_usr, qt_pwd)

    testApi = TestApi()

    testApi.QtLogin(qt_usr, qt_pwd)

    GetHistDataMultiThread()

    # testApi.GetExchanges()

    # testApi.GetDataByTime()

    # TestGetAllHistData()

    testApi.QtLogout(qt_usr)

    sys.exit(0)

if __name__ == "__main__":
    main()
