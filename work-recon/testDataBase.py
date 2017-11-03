# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import pymssql

from CONFIG import *
from databaseClass import MSSQL
from toolFunc import *
from databaseFunc import *
from netdataFunc import *

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')

# 'SZ300512'

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
    
def testGetMaxMinDataTime():
    database = "MarketData"
    table = "SH600000"
    startDate, endDate = getTableDataStartEndTime(database, table, g_logFile)
    print startDate, endDate

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

def testInsertSamePrimaryValue():
    try:
        databaseObj = MSSQL()
        valueArray = [(20160101, 90103), (20160101, 90104)]
        for value in valueArray:        
            insertStr = "insert into [MarketData].[dbo].[SH600000] (TDATE, TIME) values(" + str(value[0]) +", " + str(value[1]) +")"
            try:
                databaseObj.ExecStoreProduce(insertStr)
            except Exception as e:
                repeatInsertError = "Violation of PRIMARY KEY constraint"
                if repeatInsertError not in e[1]:                                        
                    break
            
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

def addPrimaryKeyToDatabase():
    try:
        database = "MarketData"
        secodeArray = getSecodeInfoFromTianRuan(g_logFile)

        infoStr = "Secode Numb : " + str(len(secodeArray)) + '\n'
        LogInfo(g_logFile, infoStr)   

        completeDatabaseTable(database, secodeArray, g_logFile)
        addPrimaryKey(database, g_logFile)
        
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "AddPrimaryKeyToDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(infoStr))    

def testConnectRemoteDatabaseServer():
    try:
        remoteServer = "192.168.211.165"
        localServer = '127.0.0.1'
        user = 'sa'
        pwd = 'sasa'
        db = 'TestData'
        # conn = pymssql.connect(host=remoteServer, user=user,password=pwd,database=db, \
        #                        port='1433',timeout=5,login_timeout=2,charset="utf8")  

        databaseObj = MSSQL(host=remoteServer)

        databaseObj.CloseConnect()

    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "__Main__ Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(infoStr))
     
if __name__ == "__main__":
    try:
        # changeDatabase()
        # testInsertSamePrimaryValue()
        testConnectRemoteDatabaseServer()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "__Main__ Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        LogInfo(g_logFile, infoStr)

    
    
    