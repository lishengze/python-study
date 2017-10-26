# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count

from toolFunc import *
from testFunc import *
from example import MSSQL
from CONFIG import *
import datetime

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
        code = 'SH000001'
        startDate = "20160901" 
        endDate = "20170901"
        tslStr = getMarketDataTslStr(code, startDate, endDate, g_logFile);
        curs.execute(tslStr)
        result = curs.fetchall()
        # print len(result)
        curs.close()
        conn.close()
        return result        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetMarketDataTslStr Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr)      

def testInserData():
    try:
        starttime = datetime.datetime.now()
        infoStr = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"

        databaseObj = MSSQL() 
        result = testGetStockData()
        print len(result)

        desTableName = '[HistData].[dbo].[LCY_STK_01MS_1]'
        for i in range(len(result)):
            insertStr = getInsertStockDataStr(result[i], desTableName)
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
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr)   
  
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
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr) 

def testRefreshTestDatabase():
    refreshTestDatabase("TestData", 4, g_logFile)
    
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
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr)   ,

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

if __name__ == "__main__":
    # testGetSecodeInfo()
    # testGetStockData()
    # testInserData()
    # testGetStockGoMarkerTime()
    # testRefreshTestDatabase()
    # testMultiThreadConnect()
    testGetAllStockDataCostDays()
    # testMultiThreadWriteData()
    
    