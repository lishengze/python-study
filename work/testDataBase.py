# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import pymssql

from CONFIG import *
from toolFunc import *

from database import Database
from tinysoft import TinySoft

from market_database import MarketDatabase

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')
g_writeLogLock = threading.Lock()

def test_insert_data():
        starttime = datetime.datetime.now()
        log_str = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
        LogInfo(g_logFile, log_str)   

        database_host = 'localhost'
        database_name = 'TestData'
        database_obj = Database(host=database_host, db=database_name)

        tinysoft_obj = TinySoft(g_logFile, g_writeLogLock)
        netconn_obj = tinysoft_obj

        secode_all = netconn_obj.getSecodeInfo()
        secode = secode_all[10]
        start_time = 20171001
        end_time = 20171101

        market_data = netconn_obj.getStockData(secode, start_time, end_time)
        print len(market_data)

        database_name = "TestData"
        table_name = secode
        
        table_name_array = database_obj.getDatabaseTableInfo(database_name)
        complete_table_name = u'[' + database_name + '].[dbo].['+ table_name +']'
        if table_name not in table_name_array:            
            database_obj.createTableByName(complete_table_name)

        for cur_market_data in market_data:
            insert_str = netconn_obj.getInsertStockDataStr(cur_market_data, complete_table_name)
            database_obj.changeDatabase(insert_str)
          
        endtime = datetime.datetime.now()
        cost_time = (endtime - starttime).seconds
        log_str = "++++++++++ End Time: " + str(endtime) \
                + ' Sum Cost Time: ' + str(cost_time)  + "s ++++++++\n"  
        LogInfo(g_logFile, log_str)                           
    
def testGetMaxMinDataTime():
    database = "MarketData"
    table = "SH600000"
    startDate, endDate = getTableDataStartEndTime(database, table, g_logFile)
    print startDate, endDate

def testMultiThreadWriteData():
    try:
        starttime = datetime.datetime.now()
        log_str = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
        LogInfo(g_logFile, log_str)   
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

        log_str = "++++++++++ End Time: " + str(endtime) \
                + " AveTime: " + str(aveTime) + "s Sum Cost Days: " + str(sumCostDays) + " days ++++++++\n"  
        LogInfo(g_logFile, log_str)                                   
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "testMultiThreadWriteData Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, log_str)   
        raise(log_str)

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
        log_str = "[X] TestCompleteDatabase Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, log_str) 
        raise(log_str)

def testCompleteDatabase():
    try:
        database = "TestData"
        tableArray = ["SH666666", "SH700000"]
        completeDatabaseTable(database, tableArray, g_logFile)
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "[X] TestCompleteDatabase Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(g_logFile, log_str) 
        raise(log_str)

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
        log_str = "TestInsertSamePrimaryValue Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(log_str))

def changeDatabase():
    try:
        database = "MarketData"
        secodeArray = getSecodeInfoFromTianRuan(g_logFile)

        log_str = "Secode Numb : " + str(len(secodeArray)) + '\n'
        LogInfo(g_logFile, log_str)   

        refreshDatabase(database, secodeArray, g_logFile)
        addPrimaryKey(database, g_logFile)
        
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "ChangeDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(log_str))

def addPrimaryKeyToDatabase():
    try:
        database = "MarketData"
        secodeArray = getSecodeInfoFromTianRuan(g_logFile)

        log_str = "Secode Numb : " + str(len(secodeArray)) + '\n'
        LogInfo(g_logFile, log_str)   

        completeDatabaseTable(database, secodeArray, g_logFile)
        addPrimaryKey(database, g_logFile)
        
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "AddPrimaryKeyToDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(log_str))    

def testConnectRemoteDatabaseServer():
    try:
        remoteServer = "192.168.211.165"
        databaseName = 'MarketData'
        databaseObj = Database(host=remoteServer, db=databaseName)

        databaseTableInfo = databaseObj.getDatabaseTableInfo(databaseName)
        print len(databaseTableInfo)

    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "__Main__ Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        raise(Exception(log_str))

def testRefreshDatabase():
    remoteServer = '192.168.211.165'
    localServer = 'localhost'

    databaseName = 'MarketData'
    databaseObj = Database(host=localServer, db=databaseName)

    tinySoftObj = TinySoft(g_logFile, g_writeLogLock)
    netConnObj = tinySoftObj

    secodeArray = netConnObj.getSecodeInfo()

    infoStr = "Secode Numb : " + str(len(secodeArray)) + '\n'
    LogInfo(g_logFile, infoStr)   

    databaseObj.refreshDatabase(databaseName, secodeArray)

def cleanMarketDatabase():
    database_name = "MarketDataTest"
    database_obj = MarketDatabase(db=database_name)
    table_array = database_obj.getDatabaseTableInfo()
    for table in table_array:
        database_obj.dropTableByName(table)

def testMarketDatabase():
    data_type = "MarketDataTest"
    marketdatabase_obj = MarketDatabase(db=data_type)
    tablename = "1"
    table_starttime , table_endtime = marketdatabase_obj.getTableDataStartEndTime(tablename)
    ori_starttime = 20171114.40
    ori_endtime = getDateNow(data_type)

    print 'ori_time'
    print ori_starttime, ori_endtime
    print 'table_time'
    print table_starttime, table_endtime
    print marketdatabase_obj.getStartEndTime(ori_starttime, ori_endtime, table_starttime, table_endtime)

if __name__ == "__main__":
    try:
        # changeDatabase()
        # testInsertSamePrimaryValue()
        # testConnectRemoteDatabaseServer()
        # testRefreshDatabase()
        # test_insert_data()
        # cleanMarketDatabase()
        testMarketDatabase()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "__Main__ Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        LogInfo(g_logFile, log_str)

    
    
    