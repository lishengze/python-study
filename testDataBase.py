# -*- coding: UTF-8 -*-
import time

import os, sys
import traceback
import pyodbc

import datetime
import threading

from CONFIG import *
from toolFunc import *

from wind import Wind

from database import Database

from weight_database import WeightDatabase
from weight_datanet import WeightTinySoft

from market_database import MarketDatabase
from market_datanet import MarketTinySoft

from industry_database import IndustryDatabase
from industry_datanet import IndustryNetConnect

g_writeLogLock = threading.Lock()
g_logFileName = os.getcwd() + '\log.txt'
g_logFile = open(g_logFileName, 'w')
g_susCount = 0
g_susCountLock = threading.Lock()

def get_database_obj(database_name, host='localhost'):
    if "WeightData" in database_name:
        return WeightDatabase(host=host, db=database_name)

    if "MarketData" in database_name:
        return MarketDatabase(host=host, db=database_name)

    if "IndustryData" in database_name:
        return IndustryDatabase(host=host, db=database_name)

def get_netconn_obj(database_type):
    if "WeightData" in database_type:
        return WeightTinySoft(database_type)

    if "MarketData" in database_type:
        return MarketTinySoft(database_type) 

    if "IndustryData" in database_type:
        return IndustryNetConnect(database_type)     

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
        # remoteServer = "192.168.211.165"
        remoteServer = "localhost"
        databaseName = 'MarketData'
        databaseObj = Database(host=remoteServer, db=databaseName)

        databaseTableInfo = databaseObj.getDatabaseTableInfo()
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

def testGetLatestData():
    timeType = "day"
    host = "localhost"
    # host = "192.168.211.165"
    data_type = "MarketData" + "_" + timeType
    database_obj = get_database_obj(data_type, host=host)
    # secode = "SH000016"
    secode = "SH600000"
    latest_data = database_obj.getLatestData(secode)
    # print_data("latest_data: ", latest_data)
    latest_data_array = database_obj.getAllLatestData([secode])
    print  latest_data_array[secode]

def testTimeData():
    timeType = "1m"
    host = "localhost"
    # host = "192.168.211.165"
    data_type = "MarketData" + "_" + timeType
    database_obj = get_database_obj(data_type, host=host)
    netconn_obj = get_netconn_obj(data_type)

    ori_startdate = 20141108
    ori_enddate = 20160608

    trade_time_array = get_index_tradetime(netconn_obj,ori_startdate, ori_enddate)
    print "trade_time_array numb: ", len(trade_time_array)

    tablename_array = database_obj.getDatabaseTableInfo()
    testData = {}
    for tablename in tablename_array:
        curdata = []
        dataNumb = database_obj.get_datacount(tablename)
        date = database_obj.getStartEndDate(tablename)
        curdata.append(dataNumb)
        curdata.append(date)
        if len(date) !=0 and date[0] != None and date[1] != None:
            # print date[0], date[1]
            index_data= get_sub_index_tradetime(trade_time_array, date[0], date[1])
            curdata.append("indexDatanumb: ")
            curdata.append(len(index_data))          
            if dataNumb != len(index_data):
                curdata.append("FALSE")
            else:
                curdata.append("TRUE")
        testData[tablename] = curdata

    print_dict_data("testData: ", testData)

if __name__ == "__main__":
    try:
        # changeDatabase()
        # testInsertSamePrimaryValue()
        # testConnectRemoteDatabaseServer()
        # testRefreshDatabase()
        # test_insert_data()
        # cleanMarketDatabase()
        # testMarketDatabase()
        # testGetLatestData()
        testTimeData()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "__Main__ Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        LogInfo(g_logFile, log_str)

    
    
