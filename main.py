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

def getSusCount():    
    global g_susCountLock, g_susCount
    g_susCountLock.acquire()
    g_susCount = g_susCount + 1
    tmpSusCount = g_susCount
    g_susCountLock.release()      
    return tmpSusCount

def recordInfoWithLock(info_str):
    global g_writeLogLock, g_logFile
    g_writeLogLock.acquire()
    print info_str
    g_logFile.write(info_str + '\n')
    g_writeLogLock.release()      

def writeDataToDatabase(result_array, source, mainthread_database_obj):
    try:
        database_obj = get_database_obj(mainthread_database_obj.db, mainthread_database_obj.host)        
        table_name = source
        database_obj.completeDatabaseTable([table_name])        
        for item in result_array:
            database_obj.insert_data(item, table_name)

        tmp_successcount = getSusCount()

        info_str = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "Source: " + source +" Write " + str(len(result_array)) +" Items to " + database_obj.db +", CurSuccessCount:  " + str(tmp_successcount) + " \n" 

        recordInfoWithLock(info_str)        
    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : \n" + exception_info
        recordInfoWithLock(info_str)  

def singleThreadWriteDataToDatabase(result_array, source, mainthread_database_obj):
    database_obj = mainthread_database_obj        
    table_name = source  
    for item in result_array:
        database_obj.insert_data(item, table_name)

def startWriteThread(netdata_array, source_array, database_obj):
    threads = []
    for i in range(len(netdata_array)):
        tmp_thread = threading.Thread(target=writeDataToDatabase, args=(netdata_array[i], str(source_array[i]), database_obj,))
        threads.append(tmp_thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()      
    
    print ("threading.active_count(): %d\n") % (threading.active_count())

def MultiThreadWriteData(data_type, source_conditions, database_host=DATABASE_HOST):
    starttime = datetime.datetime.now()
    info_str = "+++++++++ "+ data_type +" Start Time: " + str(starttime) + " +++++++++++\n"
    LogInfo(g_logFile, info_str)

    database_name = data_type

    database_obj = get_database_obj(database_name, host=database_host)
    netconn_obj = get_netconn_obj(data_type)

    # database_obj.clearDatabase()

    source = netconn_obj.get_sourceinfo(source_conditions)
    tablename_array = netconn_obj.get_tablename(source_conditions)

    source = database_obj.filter_source(source)
    tablename_array = database_obj.filter_tableArray(tablename_array)
    
    database_obj.completeDatabaseTable(tablename_array)
    latest_data = database_obj.getAllLatestData(tablename_array)

    # secode = "SH600021"
    # print "latest_data[SH600021]: ", latest_data[secode][0]

    thread_count = 12
    info_str = "Table Numb : " + str(len(tablename_array)) + '\n'
    LogInfo(g_logFile, info_str)

    condition_count = 0
    tmp_netdata_array = []
    tmp_tablename_array = []

    sus_secode = []

    print 0

    if "MarketData" in data_type:
        com_tradetime_array = get_index_tradetime(netconn_obj, source_conditions[0], source_conditions[1])

    print 1

    for i in range(len(tablename_array)):        
        cur_tablename = tablename_array[i]
        cur_source = netconn_obj.get_cursource(cur_tablename, source)
        database_transed_conditions = database_obj.get_transed_conditions(cur_tablename, cur_source)

        for j in range(len(database_transed_conditions)):
            cur_condition = database_transed_conditions[j]
            ori_netdata = netconn_obj.get_netdata(cur_condition)
            isfirstInterval = False

            if j == 0 and ori_netdata is None:
                info_str = "[C] Source: " + str(cur_source) + " has no data under conditons: " + str(cur_condition) +" \n"
                LogInfo(g_logFile, info_str) 
            else:
                if ori_netdata is None:
                    ori_netdata = []
                if j == 0:
                    isfirstInterval = True
                if "MarketData" in data_type:
                    tradetime_array = get_sub_index_tradetime(com_tradetime_array, cur_condition[1], cur_condition[2])

                condition_count = condition_count + 1
                info_str = "[B] Source: " + str(cur_condition) + ", OriDataNumb: " + str(len(ori_netdata)) 
                # info_str += ", latest_data[" + cur_tablename + "].size: " + str(len(latest_data[cur_tablename]))
                # info_str += ", sourceCount: "+ str(i+1) + ", conIndex: "+ str(j) +"\n"
                # LogInfo(g_logFile, info_str)

                old_oridata_numb = len(ori_netdata)
                if "MarketData" in data_type:
                    complete_data = add_suspdata(tradetime_array, ori_netdata, isfirstInterval, latest_data[cur_tablename])
                    info_str += ", CompleteDataNumb: " + str(len(complete_data))
                    ori_netdata = complete_data
                    if len(complete_data) != old_oridata_numb:
                        sus_secode.append([cur_tablename, len(complete_data) - old_oridata_numb])
                
                tmp_netdata_array.append(ori_netdata)
                tmp_tablename_array.append(cur_tablename)

                if (condition_count % thread_count == 0) or (i == len(tablename_array)-1 and j == len(database_transed_conditions) -1):
                    startWriteThread(tmp_netdata_array, tmp_tablename_array, database_obj)
                    tmp_netdata_array = []
                    tmp_tablename_array = []                 

                info_str += ", sourceCount: "+ str(i+1) + ", conIndex: "+ str(j) +"\n"
                LogInfo(g_logFile, info_str)
        if len(database_transed_conditions) == 0:
                info_str = "[D] source: " + str(cur_source) + " already has data under current conditons: " + str(cur_source) +" \n"
                LogInfo(g_logFile, info_str)

    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    if len(tablename_array) == 0:
        aveTime = costTime
    else:
        aveTime = costTime / len(tablename_array)

    print_data("sus_secode: ", sus_secode)
    info_str = "++++++++++"+ data_type +" End Time: " + str(endtime) \
            + " SumCostTime: " + str(costTime) + "s, AveCostTime: " + str(aveTime) + "s ++++++++\n"
    LogInfo(g_logFile, info_str)      

def download_data():
    # data_type = "MarketDataTest"
    # data_type = "WeightDataTest"
    # data_type = "IndustryDataTest"
    # data_type = "IndustryData"
    data_type = "WeightData"
    # data_type = "MarketData"
    # host = "localhost"
    host = "192.168.211.165"
    # time_frequency = "day" 
    # data_type = "MarketData" + "_" + time_frequency   
    ori_startdate = 20171101
    ori_enddate = getDateNow(data_type)    
    MultiThreadWriteData(data_type, [ori_startdate, ori_enddate], database_host=host)

def download_Marketdata():
    # time_frequency = ["day", "1m", "5m", "10m", "30m", "60m", "120m", "week", "month"]
    # time_frequency = ["5m", "10m", "30m", "60m", "120m", "week", "month"]
    time_frequency = ["1m"]
    # host = "192.168.211.165"
    host = "localhost"
    ori_startdate = 20141108
    ori_enddate = 20160608

    for timeType in time_frequency:         
        data_type = "MarketData" + "_" + timeType
        # ori_enddate = getDateNow(data_type)   
        MultiThreadWriteData(data_type, [ori_startdate, ori_enddate], database_host=host)  
        g_susCount = 0

def test_get_tradetime_byindex():
    # time_frequency = ["day", "1m", "5m", "10m", "30m", "60m", "120m", "week", "month"]
    # time_frequency = ["5m", "10m", "30m", "60m", "120m", "week", "month"]
    time_frequency = ["day"]
    # host = "192.168.211.165"
    host = "localhost"
    ori_startdate = 20140508
    ori_enddate = 20151208

    for timeType in time_frequency:         
        data_type = "MarketData" + "_" + timeType
        database_obj = get_database_obj(data_type, host=host)
        netconn_obj = get_netconn_obj(data_type)
        # ori_enddate = getDateNow(data_type)   
        get_tradetime_byindex(netconn_obj, database_obj, [ori_startdate, ori_enddate])  

def test_complete_susdata():
    timeType = "day"
    host = "localhost"
    ori_startdate = 20141108
    ori_enddate = 20151108
    data_type = "MarketData" + "_" + timeType
    database_obj = get_database_obj(data_type, host=host)
    netconn_obj = get_netconn_obj(data_type)
    # ori_enddate = getDateNow(data_type)   

    # database_obj.clearDatabase()

    source_conditions = [ori_startdate, ori_enddate]
    # tradetime_array = get_tradetime_byindex(netconn_obj, database_obj, source_conditions)  
    com_tradetime_array = get_index_tradetime(netconn_obj, ori_startdate, ori_enddate)
    # print_data("tradetime_array: ", tradetime_array)
    print "com_tradetime_array.size: ", len(com_tradetime_array)

    secode = "SZ002578"
    # database_obj.completeDatabaseTable([secode])
    cur_condition = [secode, ori_startdate, ori_enddate]

    tradetime_array = get_sub_index_tradetime(com_tradetime_array, cur_condition[1], cur_condition[2])
    print "tradetime_array.size: ", len(tradetime_array)

    ori_netdata = netconn_obj.get_netdata(cur_condition) 
    # print_data("ori_netdata: ", ori_netdata)
    # print "ori_netdata.size: ", len(ori_netdata)

    ori_time_array = get_time_array(ori_netdata)
    missing_time_array = get_missing_time_array(tradetime_array, ori_time_array)
    # print_data("ori_time_array: ",  ori_time_array)
    print_data("missing_time_array: ", missing_time_array)
    # print "missing_time_array.size: ", len(missing_time_array)
    
    complete_data = add_suspdata(tradetime_array, ori_netdata, isfirstInterval=True)
    complete_time_array = get_time_array(complete_data)
    # print_data("complete_data: ", complete_data)
    # print "complete_data.size: ", len(complete_data)
    # print_data("complete_time_array: ", complete_time_array)

    com_missing_time_array = get_missing_time_array(tradetime_array, complete_time_array)
    print_data("com_missing_time_array.size: ", com_missing_time_array)
    # print "com_missing_time_array.size: ", len(com_missing_time_array)

if __name__ == "__main__":
    starttime = datetime.datetime.now()
    info_str = "********** Main Start Time: " + str(starttime) + " **********\n"
    LogInfo(g_logFile, info_str)

    try:
        download_Marketdata()        
        # download_data()
        # test_get_tradetime_byindex()
        # test_complete_susdata()
    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "__Main__ Failed" \
                + "[E] Exception : \n" + exception_info
        recordInfoWithLock(info_str)

        connFailedError = "Communication link failure---InternalConnect"
        driver_error = "The dirver did not supply an error"
        tiny_error = "self.curs.execute(tsl_str)"
        connFailedWaitTime = 10
        if connFailedError in info_str \
        or driver_error in info_str \
        or tiny_error in info_str:
            time.sleep(connFailedWaitTime)
            info_str = "[RS] MultiThreadWriteData  Restart : \n"
            recordInfoWithLock(info_str)
            download_Marketdata()

    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    info_str = "++++++++++ Main End Time: " + str(endtime) + " SumCostTime: " + str(costTime/60) + " m **********\n"
    LogInfo(g_logFile, info_str)      