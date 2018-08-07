# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime

from CONFIG import *
from databaseClass import MSSQL
from func_tool import *
from databaseFunc import *
from netdataFunc import *

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')

# 'SZ300512'
def testGetSecodeInfo():
    secodeInfo = getSecodeInfoFromTianRuan(g_logFile)

    print len(secodeInfo[0])
    print type (secodeInfo[0])
    secode = str(secodeInfo[1][0])
    print secode[0:2], secode[2:]

def testGetStockData():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        code = 'SH600023'
        startDate = "20131030" 
        endDate = "20131218"
        tslStr = getMarketDataTslStr(code, startDate, endDate, g_logFile);
        curs.execute(tslStr)
        result = curs.fetchall()
        print len(result)
        print result[0][0] == -1
        curs.close()
        conn.close()
        return result
    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "TestGetStockData Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        # LogInfo(g_logFile, infoStr)     
        raise(Exception(infoStr)) 

def testInserData():
    try:
        starttime = datetime.datetime.now()
        infoStr = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"

        databaseObj = MSSQL() 
        result = testGetStockData()
        print len(result)

        desTableName = '[HistData].[dbo].[LCY_STK_01MS_1]'
        for i in range(len(result)):
            insertStr = getInsertStockDataStr(result[i], desTableName, g_logFile)
            insertRst = databaseObj.ExecStoreProduce(insertStr)
          
        databaseObj.CloseConnect()

        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        infoStr = "++++++++++ End Time: " + str(endtime) \
                + ' Sum Cost Time: ' + str(deletaTime.seconds)  + "s ++++++++\n"  
        LogInfo(g_logFile, infoStr)                           
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "TestInserData Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, infoStr)  
        raise(infoStr)
  
def testMultiThreadConnect():
    try:
        thread_count = 2
        threads = []

        for i in range(thread_count):

            tmpThread = threading.Thread(target=simpleConnect, args=(g_logFile,))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                + "TestMultiThread Failed" + "\n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, infoStr) 
        raise(infoStr)

def testRefreshTestDatabase():
    refreshTestDatabase("TestData", 4, g_logFile)
    
def testGetMaxMinDataTime():
    database ="MarketData"
    table = "SH600000"
    startDate, endDate = getTableDataStartEndTime(database, table, g_logFile)
    print startDate, endDate

def testGetAllStockDataCostDays():
    getAllStockDataCostDays(28, g_logFile)

def testMultiThreadWriteData():
    try:
        starttime = datetime.datetime.now()
        infoStr = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
        LogInfo(g_logFile, infoStr)   
        thread_count = 8
        threads = []

        result = testGetStockData()
        print 'result rows: '+ str(len(result))

        databaseName = "TestData"
        refreshTestDatabase(databaseName, thread_count, g_logFile)
        
        for i in range(thread_count):
            tableName = str(i)
            desTableName = "["+ databaseName +"].[dbo].[" + tableName + "]"
            print desTableName
            tmpThread = threading.Thread(target=writeDataToDatabase, args=(result, desTableName, g_logFile))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()                          

        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        aveTime = deletaTime.seconds / thread_count
        sumCostDays = getAllStockDataCostDays(aveTime, g_logFile)

        infoStr = "++++++++++ End Time: " + str(endtime) \
                + " AveTime: " + str(aveTime) + "s Sum Cost Days: " + str(sumCostDays) + " days ++++++++\n"  
        LogInfo(g_logFile, infoStr)                                   
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "testMultiThreadWriteData Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, infoStr)   
        raise(infoStr)

def testGetStockGoMarkerTime():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        result = getStockGoMarkerTime(curs, '', g_logFile)
        curs.close()
        conn.close()
        return result
        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        exceptionInfo.decode('unicode_escape')
        LogInfo(g_logFile, exceptionInfo)  
        raise(infoStr)

def testGetTableDataStartEndTime():
    try:
        database = "TestData"
        table = "SH600000"
        startTime, endTime = getTableDataStartEndTime(database, table, g_logFile)
        if startTime is None or endTime is None:
            print 'table is Empty'
        else:
            print ("startTime: %d, endTime: %d")%(startTime, endTime)
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] TestCompleteDatabase Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, infoStr) 
        raise(infoStr)

def testCompleteDatabase():
    try:
        database = "TestData"
        tableArray = ["SH666666", "SH700000"]
        completeDatabaseTable(database, tableArray, g_logFile)
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] TestCompleteDatabase Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, infoStr) 
        raise(infoStr)

def testGetStartEndTime():
    oriTimeArray = [[20130902, 22000101],
                    [20170902, 22000101],
                    [20000000, 20170831],
                    [20000000, 20100000],
                    [20000000, 20170901],
                    [20140000, 20150000]]
    database = "TestData"
    table = "SH600000"
    for i in range(len(oriTimeArray)):
        curTimeArray = getStartEndTime(oriTimeArray[i][0], oriTimeArray[i][1], database, table, g_logFile)
        for (startDate, endDate) in curTimeArray:   
            print (startDate, endDate)

def testDate():
    oriDate = 20161201
    print getYearMonthDay(oriDate)
    addDate = addOneDay(oriDate)
    print addDate
    minusDate = minusOneDay(oriDate)
    print minusDate

def testGetIntegerDateNow():
    integerDate = getIntegerDateNow(g_logFile)
    print type(integerDate)
    print integerDate

def testInsertSamePrimaryValue():
    try:
        databaseObj = MSSQL()
        insertStr = "insert into [MarketData].[dbo].[SH600000] (TDATE, TIME) values(20160101, 090103)"
        databaseObj.ExecStoreProduce(insertStr)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "TestInsertSamePrimaryValue Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(infoStr))

def changeDatabase():
    try:
        database = "MarketData"
        secodeArray = getSecodeInfoFromTianRuan(g_logFile)

        infoStr = "Secode Numb : " + str(len(secodeArray)) + '\n'
        LogInfo(g_logFile, infoStr)   

        refreshDatabase(database, secodeArray, g_logFile)
        addPrimaryKey(database, g_logFile)
        
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "ChangeDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(infoStr))
    
if __name__ == "__main__":
    try:
        # testGetSecodeInfo()
        # testGetStockData()
        # testInserData()
        # testGetStockGoMarkerTime()
        # testRefreshTestDatabase()
        # testCompleteDatabase()
        # testMultiThreadConnect()
        # testGetAllStockDataCostDays()
        # testMultiThreadWriteData()
        # testGetTableDataStartEndTime()
        # testGetStartEndTime()
        # testDate()
        # testGetIntegerDateNow()
        # testGetMaxMinDataTime()
        # changeDatabase()
        testInsertSamePrimaryValue()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "__Main__ Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(infoStr))

    
    
    