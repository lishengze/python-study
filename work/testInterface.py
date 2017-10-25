# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count

from toolFunc import *
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
        startDate = "20130901" 
        endDate = "20170902"
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
  
def simpleConnect():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        curs.close()
        conn.close()

        infoStr = "[i] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleConnect Succeed \n"
        LogInfo(g_logFile, infoStr)  
        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleConnect Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr) 

def simpleExc(curs):
    try:
        tslStr = u"name:='A股';StockID:=getbk(name);return StockID;"
        curs.execute(tslStr)
        result = curs.fetchall()
        print len(result)
        infoStr = "[i] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleExc Succeed \n"
        LogInfo(g_logFile, infoStr)          
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleExc Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr)     

def testMultiThreadConnect():
    try:
        thread_count = 2
        threads = []

        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()

        for i in range(thread_count):
            # tmpThread = threading.Thread(target=simpleExc, args=(curs,))
            tmpThread = threading.Thread(target=simpleConnect)
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        curs.close()
        conn.close()
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                + "TestMultiThread Failed" + "\n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr) 

def writeDataToDatabase(databaseObj, result, desTableName):
    try:
        starttime = datetime.datetime.now()

        for i in range(len(result)):
            insertStr = getInsertStockDataStr(result[i], desTableName)
            insertRst = databaseObj.ExecStoreProduce(insertStr)

        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        infoStr = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "WriteDataToDatabase Succeed Cost " + str(deletaTime.seconds) + "s \n" 
        LogInfo(g_logFile, infoStr) 
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr)              

def refreshTestDatabase(databaseName, tableNumb):
    try:
        databaseObj = MSSQL() 
        tableInfo = GetDatabaseTableInfo(databaseName)
        # print tableInfo
        for i in range(tableNumb):
            tableName = str(i)
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

            if tableName in tableInfo:
                dropTableByName(databaseObj, completeTableName)
                # print completeTableName
            createTableByName(databaseObj, completeTableName)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(g_logFile, infoStr)  

def testRefreshTestDatabase():
    refreshTestDatabase(4)

def testMultiThreadWriteData():
    try:
        starttime = datetime.datetime.now()
        infoStr = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
        thread_count = 2
        threads = []

        databaseObj = MSSQL() 
        result = testGetStockData()
        print 'result rows: '+ str(len(result))

        databaseName = "TestData"
        refreshTestDatabase(databaseName, thread_count)
        
        for i in range(thread_count):
            tableName = str(i)
            desTableName = "["+ databaseName +"].[dbo].[" + tableName + "]"
            print desTableName
            tmpThread = threading.Thread(target=writeDataToDatabase, args=(databaseObj, result, desTableName))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()                
          
        databaseObj.CloseConnect()

        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        infoStr = "++++++++++ End Time: " + str(endtime) \
                + ' Sum Cost Time: ' + str(deletaTime.seconds)  + "s ++++++++\n"  
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
    # testMultiThread()
    # testInserData()
    # testGetStockGoMarkerTime()
    # testRefreshTestDatabase()
    testMultiThreadWriteData()