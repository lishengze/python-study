# -*- coding: UTF-8 -*-
import time

import os, sys
import traceback
import pyodbc

import datetime
import threading

from CONFIG import *
from func_tool import *

from database import Database

from weight_database import WeightDatabase
from weight_datanet import WeightTinySoft

from market_database import MarketDatabase
from market_datanet import MarketTinySoft

from market_info_database import MarketInfoDatabase

from operator import itemgetter, attrgetter
from math import *
import random

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

def get_netconn_obj(database_type):
    if "WeightData" in database_type:
        return WeightTinySoft(database_type)

    if "MarketData" in database_type:
        return MarketTinySoft(database_type) 

    # if "IndustryData" in database_type:
    #     return IndustryNetConnect(database_type)     

# def test_insert_data():
#         starttime = datetime.datetime.now()
#         log_str = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
#         LogInfo(g_logFile, log_str)   

#         database_host = 'localhost'
#         database_name = 'TestData'
#         database_obj = Database(host=database_host, db=database_name)

#         tinysoft_obj = TinySoft(g_logFile, g_writeLogLock)
#         netconn_obj = tinysoft_obj

#         secode_all = netconn_obj.getSecodeInfo()
#         secode = secode_all[10]
#         start_time = 20171001
#         end_time = 20171101

#         market_data = netconn_obj.getStockData(secode, start_time, end_time)
#         print len(market_data)

#         database_name = "TestData"
#         table_name = secode
        
#         table_name_array = database_obj.getDatabaseTableInfo(database_name)
#         complete_table_name = u'[' + database_name + '].[dbo].['+ table_name +']'
#         if table_name not in table_name_array:            
#             database_obj.createTableByName(complete_table_name)

#         for cur_market_data in market_data:
#             insert_str = netconn_obj.getInsertStockDataStr(cur_market_data, complete_table_name)
#             database_obj.changeDatabase(insert_str)
          
#         endtime = datetime.datetime.now()
#         cost_time = (endtime - starttime).seconds
#         log_str = "++++++++++ End Time: " + str(endtime) \
#                 + ' Sum Cost Time: ' + str(cost_time)  + "s ++++++++\n"  
#         LogInfo(g_logFile, log_str)                           
    
# def testGetMaxMinDataTime():
#     database = "MarketData"
#     table = "SH600000"
#     startDate, endDate = getTableDataStartEndTime(database, table, g_logFile)
#     print startDate, endDate

# def testMultiThreadWriteData():
#     try:
#         starttime = datetime.datetime.now()
#         log_str = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
#         LogInfo(g_logFile, log_str)   
#         thread_count = 8
#         threads = []

#         result = testGetStockData()
#         print 'result rows: '+ str(len(result))

#         databaseName = "TestData"
#         refreshTestDatabase(databaseName, thread_count, g_logFile)
        
#         for i in range(thread_count):
#             tableName = str(i)
#             desTableName = "["+ databaseName +"].[dbo].[" + tableName + "]"
#             print desTableName
#             tmpThread = threading.Thread(target=writeDataToDatabase, args=(result, desTableName, g_logFile))
#             threads.append(tmpThread)

#         for thread in threads:
#             thread.start()

#         for thread in threads:
#             thread.join()                          

#         endtime = datetime.datetime.now()
#         deletaTime = endtime - starttime
#         aveTime = deletaTime.seconds / thread_count
#         sumCostDays = getAllStockDataCostDays(aveTime, g_logFile)

#         log_str = "++++++++++ End Time: " + str(endtime) \
#                 + " AveTime: " + str(aveTime) + "s Sum Cost Days: " + str(sumCostDays) + " days ++++++++\n"  
#         LogInfo(g_logFile, log_str)                                   
#     except Exception as e:
#         exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
#         log_str = "testMultiThreadWriteData Failed \n" \
#                 + "[E] Exception : \n" + exceptionInfo
#         LogInfo(g_logFile, log_str)   
#         raise(log_str)

# def testGetTableDataStartEndTime():
#     try:
#         database = "TestData"
#         table = "SH600000"
#         startTime, endTime = getTableDataStartEndTime(database, table, g_logFile)
#         if startTime is None or endTime is None:
#             print 'table is Empty'
#         else:
#             print ("startTime: %d, endTime: %d")%(startTime, endTime)
#     except Exception as e:
#         exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
#         log_str = "[X] TestCompleteDatabase Failed \n" \
#                 + "[E] Exception : \n" + exceptionInfo
#         LogInfo(g_logFile, log_str) 
#         raise(log_str)

# def testCompleteDatabase():
#     try:
#         database = "TestData"
#         tableArray = ["SH666666", "SH700000"]
#         completeDatabaseTable(database, tableArray, g_logFile)
#     except Exception as e:
#         exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
#         log_str = "[X] TestCompleteDatabase Failed \n" \
#                 + "[E] Exception : \n" + exceptionInfo
#         LogInfo(g_logFile, log_str) 
#         raise(log_str)

# def testGetStartEndTime():
#     oriTimeArray = [[20130902, 22000101],
#                     [20170902, 22000101],
#                     [20000000, 20170831],
#                     [20000000, 20100000],
#                     [20000000, 20170901],
#                     [20140000, 20150000]]
#     database = "TestData"
#     table = "SH600000"
#     for i in range(len(oriTimeArray)):
#         curTimeArray = getStartEndTime(oriTimeArray[i][0], oriTimeArray[i][1], database, table, g_logFile)
#         for (startDate, endDate) in curTimeArray:   
#             print (startDate, endDate)

# def testInsertSamePrimaryValue():
#     try:
#         databaseObj = MSSQL()
#         valueArray = [(20160101, 90103), (20160101, 90104)]
#         for value in valueArray:        
#             insertStr = "insert into [MarketData].[dbo].[SH600000] (TDATE, TIME) values(" + str(value[0]) +", " + str(value[1]) +")"
#             try:
#                 databaseObj.ExecStoreProduce(insertStr)
#             except Exception as e:
#                 repeatInsertError = "Violation of PRIMARY KEY constraint"
#                 if repeatInsertError not in e[1]:                                        
#                     break
            
#         databaseObj.CloseConnect()
#     except Exception as e:
#         exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
#         log_str = "TestInsertSamePrimaryValue Failed \n" \
#                 + "[E] Exception :  \n" + exceptionInfo  
#         raise(Exception(log_str))

# def changeDatabase():
#     try:
#         database = "MarketData"
#         secodeArray = getSecodeInfoFromTianRuan(g_logFile)

#         log_str = "Secode Numb : " + str(len(secodeArray)) + '\n'
#         LogInfo(g_logFile, log_str)   

#         refreshDatabase(database, secodeArray, g_logFile)
#         addPrimaryKey(database, g_logFile)
        
#     except Exception as e:
#         exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
#         log_str = "ChangeDatabase Failed \n" \
#                 + "[E] Exception :  \n" + exceptionInfo  
#         raise(Exception(log_str))

# def addPrimaryKeyToDatabase():
#     try:
#         database = "MarketData"
#         secodeArray = getSecodeInfoFromTianRuan(g_logFile)

#         log_str = "Secode Numb : " + str(len(secodeArray)) + '\n'
#         LogInfo(g_logFile, log_str)   

#         completeDatabaseTable(database, secodeArray, g_logFile)
#         addPrimaryKey(database, g_logFile)
        
#     except Exception as e:
#         exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
#         log_str = "AddPrimaryKeyToDatabase Failed \n" \
#                 + "[E] Exception :  \n" + exceptionInfo  
#         raise(Exception(log_str))    

# def testConnectRemoteDatabaseServer():
#     try:
#         # remoteServer = "192.168.211.165"
#         remoteServer = "localhost"
#         databaseName = 'MarketData'
#         databaseObj = Database(host=remoteServer, db=databaseName)

#         databaseTableInfo = databaseObj.getDatabaseTableInfo()
#         print len(databaseTableInfo)

#     except Exception as e:
#         exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
#         log_str = "__Main__ Failed \n" \
#                 + "[E] Exception :  \n" + exceptionInfo
#         raise(Exception(log_str))

# def testRefreshDatabase():
#     remoteServer = '192.168.211.165'
#     localServer = 'localhost'

#     databaseName = 'MarketData'
#     databaseObj = Database(host=localServer, db=databaseName)

#     tinySoftObj = TinySoft(g_logFile, g_writeLogLock)
#     netConnObj = tinySoftObj

#     secodeArray = netConnObj.getSecodeInfo()

#     infoStr = "Secode Numb : " + str(len(secodeArray)) + '\n'
#     LogInfo(g_logFile, infoStr)   

#     databaseObj.refreshDatabase(databaseName, secodeArray)

# def cleanMarketDatabase():
#     database_name = "MarketDataTest"
#     database_obj = MarketDatabase(db=database_name)
#     table_array = database_obj.getDatabaseTableInfo()
#     for table in table_array:
#         database_obj.dropTableByName(table)

# def testMarketDatabase():
#     data_type = "MarketDataTest"
#     marketdatabase_obj = MarketDatabase(db=data_type)
#     tablename = "1"
#     table_starttime , table_endtime = marketdatabase_obj.getTableDataStartEndTime(tablename)
#     ori_starttime = 20171114.40
#     ori_endtime = getDateNow(data_type)

#     print 'ori_time'
#     print ori_starttime, ori_endtime
#     print 'table_time'
#     print table_starttime, table_endtime
#     print marketdatabase_obj.getStartEndTime(ori_starttime, ori_endtime, table_starttime, table_endtime)



# def testTimeData(timeType="day", ori_startdate=0, ori_enddate=0):
#     timeType = "day"
#     host = "localhost"
#     # host = "192.168.211.165"
#     data_type = "MarketData" + "_" + timeType
#     database_obj = get_database_obj(data_type, host=host)
#     netconn_obj = get_netconn_obj(data_type)

#     ori_startdate = 20130108
#     ori_enddate = getDateNow(data_type)  

#     trade_time_array = get_index_tradetime(netconn_obj,ori_startdate, ori_enddate)
#     print "trade_time_array numb: ", len(trade_time_array)

#     tablename_array = database_obj.getDatabaseTableInfo()
#     right_Data = {}
#     error_data = {}
#     for tablename in tablename_array:
#         curdata = []
#         dataNumb = database_obj.get_datacount(tablename)
#         date = database_obj.getStartEndDate(tablename)
#         curdata.append(dataNumb)
#         curdata.append(date)
#         if len(date) !=0 and date[0] != None and date[1] != None:
#             # print date[0], date[1]
#             index_data= get_sub_index_tradetime(trade_time_array, date[0], date[1])
#             curdata.append("indexDatanumb: ")
#             curdata.append(len(index_data))          
#             if dataNumb != len(index_data):
#                 curdata.append("FALSE")
#                 error_data[tablename] = curdata
#             else:
#                 curdata.append("TRUE")
#                 right_Data[tablename] = curdata
        

#     # print_dict_data("right_Data: ", right_Data)
#     print_dict_data("error_Data: ", error_data)

# def test_get_histdata_by_enddate():
#     timeType = "10m"
#     host = "localhost"
#     data_type = "MarketData" + "_" + timeType
#     database_obj = get_database_obj(data_type, host=host)    
#     enddate = 20180101
#     secode = "SH600000"
#     col_str = "[TDATE], [TIME], [TCLOSE], [PCTCHG], [YCLOSE]"
#     ori_data = database_obj.get_histdata_by_enddate(enddate, secode, col_str)
#     # print_data("ori_data: ", ori_data)
#     ori_data.sort(key=itemgetter(0,1), reverse = True)
#     print_data("reversed data: ", ori_data[0:10])

# def test_get_tradetime_byindex():
#     # time_frequency = ["day", "1m", "5m", "10m", "30m", "60m", "120m", "week", "month"]
#     # time_frequency = ["5m", "10m", "30m", "60m", "120m", "week", "month"]
#     time_frequency = ["day"]
#     # host = "192.168.211.165"
#     host = "localhost"
#     ori_startdate = 20140508
#     ori_enddate = 20151208

#     for timeType in time_frequency:         
#         data_type = "MarketData" + "_" + timeType
#         database_obj = get_database_obj(data_type, host=host)
#         netconn_obj = get_netconn_obj(data_type)
#         # ori_enddate = getDateNow(data_type)   
#         get_tradetime_byindex(netconn_obj, database_obj, [ori_startdate, ori_enddate])  

# def test_complete_susdata():
#     timeType = "day"
#     host = "localhost"
#     ori_startdate = 20141108
#     ori_enddate = 20151108
#     data_type = "MarketData" + "_" + timeType
#     database_obj = get_database_obj(data_type, host=host)
#     netconn_obj = get_netconn_obj(data_type)
#     # ori_enddate = getDateNow(data_type)   

#     # database_obj.clearDatabase()

#     source_conditions = [ori_startdate, ori_enddate]
#     # tradetime_array = get_tradetime_byindex(netconn_obj, database_obj, source_conditions)  
#     com_tradetime_array = get_index_tradetime(netconn_obj, ori_startdate, ori_enddate)
#     # print_data("tradetime_array: ", tradetime_array)
#     print "com_tradetime_array.size: ", len(com_tradetime_array)

#     secode = "SZ002578"
#     # database_obj.completeDatabaseTable([secode])
#     cur_condition = [secode, ori_startdate, ori_enddate]

#     tradetime_array = get_sub_index_tradetime(com_tradetime_array, cur_condition[1], cur_condition[2])
#     print "tradetime_array.size: ", len(tradetime_array)

#     ori_netdata = netconn_obj.get_netdata(cur_condition) 
#     # print_data("ori_netdata: ", ori_netdata)
#     # print "ori_netdata.size: ", len(ori_netdata)

#     ori_time_array = get_time_array(ori_netdata)
#     missing_time_array = get_missing_time_array(tradetime_array, ori_time_array)
#     # print_data("ori_time_array: ",  ori_time_array)
#     print_data("missing_time_array: ", missing_time_array)
#     # print "missing_time_array.size: ", len(missing_time_array)
    
#     complete_data = add_suspdata(tradetime_array, ori_netdata, isfirstInterval=True)
#     complete_time_array = get_time_array(complete_data)
#     # print_data("complete_data: ", complete_data)
#     # print "complete_data.size: ", len(complete_data)
#     # print_data("complete_time_array: ", complete_time_array)

#     com_missing_time_array = get_missing_time_array(tradetime_array, complete_time_array)
#     print_data("com_missing_time_array.size: ", com_missing_time_array)
#     # print "com_missing_time_array.size: ", len(com_missing_time_array)

# def test_insert_multieData():
#     database_name = "Test"
#     db_host = "192.168.211.165"
#     table_name = "test_multi_insert"

#     databaseObj = Database(host=db_host, db=database_name)    
#     complete_tablename = u'[' + database_name + '].[dbo].['+ table_name +']'
#     col_str = "(name, age, country, income)"

#     data_numb = 1000
#     value_str = ""
#     for i in range(1, data_numb):
#         value_str += "('lee', " + str(i+20) + ", 'China', " + str(random.randint(10,100)) + "),"

#     insert_str = "insert into " + complete_tablename + " " \
#                  + col_str + " values " + value_str

#     insert_str = insert_str[0:(len(insert_str)-1)]
#     # print insert_str

#     databaseObj.changeDatabase(insert_str)

def testGetLatestData():
    timeType = "10m"
    # host = "localhost"
    host = "192.168.211.165"
    data_type = "MarketData" + "_" + timeType
    database_obj = get_database_obj(data_type, host=host)
    # secode = "SH000016"
    secode = "SH600000"
    latest_data = database_obj.getLatestData(secode)
    print("latest_data: ", latest_data)

    first_data = database_obj.getFirstData(secode)
    print("first_data: ", first_data)

    # latest_data_array = database_obj.getAllLatestData([secode])
    # print (latest_data_array[secode])

def test_get_data_by_enddatetime():
    timeType = "10m"
    host = "192.168.211.165"
    data_type = "MarketData" + "_" + timeType
    database_obj = get_database_obj(data_type, host=host)
    secode = "SH600000"    
    end_date = [20160215, 111000]
    data = database_obj.get_data_by_enddatetime(secode, end_date)
    print_list('orderd data: ', data)

def test_delete_data_by_enddatetime():
    timeType = "10m"
    host = "192.168.211.165"
    data_type = "MarketData" + "_" + timeType
    database_obj = get_database_obj(data_type, host=host)
    secode = "SH600000"    
    end_date = [20160216, 111000]
    data = database_obj.delete_data_by_enddatetime(secode, end_date)
    print_list('orderd data: ', data)    

def test_get_index_seocde_list():
    dbHost = "localhost"
    database_obj = MarketInfoDatabase(host=dbHost)
    index_code = '000300'
    result = database_obj.get_index_secode_list(index_code, 'tinysoft')
    print_list('%s secode list: '%(index_code), result)

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
        # testTimeData()
        # test_get_database()
        # test_insert_multieData();
        # test_get_data_by_enddatetime()
        # test_delete_data_by_enddatetime()
        test_get_index_seocde_list()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        log_str = "__Main__ Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        # LogInfo(g_logFile, log_str)

    
    
