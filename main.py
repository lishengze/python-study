# -*- coding: UTF-8 -*-
import time

import os, sys
import traceback
import pyodbc

import datetime
import threading

from CONFIG import *
from toolFunc import *
# from databaseFunc import *
# from netdataFunc import *

from wind import Wind

from database import Database
from weight_database import WeightDatabase
from market_database import MarketDatabase
from industry_database import IndustryDatabase

from weight_datanet import WeightTinySoft
from market_datanet import MarketTinySoft
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
    info_str = "+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
    LogInfo(g_logFile, info_str)

    database_name = data_type

    database_obj = get_database_obj(database_name, host=database_host)
    netconn_obj = get_netconn_obj(data_type)

    source = netconn_obj.get_sourceinfo(source_conditions)
    tablename_array = netconn_obj.get_tablename(source_conditions)

    source = database_obj.filter_source(source)
    tablename_array = database_obj.filter_tableArray(tablename_array)
    
    thread_count = 12

    info_str = "Table Numb : " + str(len(tablename_array)) + '\n'
    LogInfo(g_logFile, info_str)

    condition_count = 0
    tmp_netdata_array = []
    tmp_tablename_array = []

    for i in range(len(tablename_array)):        
        cur_tablename = tablename_array[i]
        cur_source = netconn_obj.get_cursource(cur_tablename, source)

        database_transed_conditions = database_obj.get_transed_conditions(cur_tablename, cur_source)

        for j in range(len(database_transed_conditions)):
            cur_condition = database_transed_conditions[j]
            ori_netdata = netconn_obj.get_netdata(cur_condition)
            if ori_netdata is not None:
                condition_count = condition_count + 1

                info_str = "[B] Source: " + str(cur_condition) + ", dataNumb: " + str(len(ori_netdata)) \
                        + ' , condition_count: ' + str(condition_count) + ", sourceCount: "+ str(i+1) + "\n"
                LogInfo(g_logFile, info_str)

                tmp_netdata_array.append(ori_netdata)
                tmp_tablename_array.append(cur_tablename)

                if (condition_count % thread_count == 0) or (i == len(tablename_array)-1 and j == len(database_transed_conditions) -1):
                    startWriteThread(tmp_netdata_array, tmp_tablename_array, database_obj)
                    tmp_netdata_array = []
                    tmp_tablename_array = [] 
            else:
                info_str = "[C] Source: " + str(cur_source) + " has no data under conditons: " + str(cur_condition) +" \n"
                LogInfo(g_logFile, info_str) 
                pass
        
        if len(database_transed_conditions) == 0:
                info_str = "[C] source: " + str(cur_source) + " already has data under current conditons: " + str(cur_source) +" \n"
                LogInfo(g_logFile, info_str)

    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    if len(tablename_array) == 0:
        aveTime = costTime
    else:
        aveTime = costTime / len(tablename_array)

    info_str = "++++++++++ End Time: " + str(endtime) \
            + " SumCostTime: " + str(costTime) + " AveCostTime: " + str(aveTime) + "s ++++++++\n"
    LogInfo(g_logFile, info_str)      

def download_data():
    # data_type = "MarketDataTest"
    # data_type = "WeightDataTest"
    # data_type = "IndustryDataTest"
    data_type = "IndustryData"
    # data_type = "WeightData"
    # data_type = "MarketData"
    host = "localhost"
    # host = "192.168.211.165"
    # time_frequency = "day" 
    # data_type = "MarketData" + "_" + time_frequency   
    ori_startdate = 20171101
    ori_enddate = getDateNow(data_type)    
    MultiThreadWriteData(data_type, [ori_startdate, ori_enddate], database_host=host)

def download_Marketdata():
    time_frequency = ["day", "1m", "5m", "10m", "30m", "60m", "120m", "week", "month"]
    # time_frequency = ["10m"]
    host = "192.168.211.165"
    # host = "localhost"
    ori_startdate = 20131001

    for timeType in time_frequency:         
        data_type = "MarketData" + "_" + timeType
        ori_enddate = getDateNow(data_type)   
        MultiThreadWriteData(data_type, [ori_startdate, ori_enddate], database_host=host)  
        g_susCount = 0

if __name__ == "__main__":
    try:
        download_Marketdata()
    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "__Main__ Failed" \
                + "[E] Exception : \n" + exception_info
        recordInfoWithLock(info_str)

        connFailedError = "Communication link failure---InternalConnect"
        connFailedWaitTime = 60 * 5
        if connFailedError in info_str:
            time.sleep(connFailedWaitTime)
            info_str = "[RS] MultiThreadWriteData  Restart : \n"
            recordInfoWithLock(info_str)
            download_Marketdata()