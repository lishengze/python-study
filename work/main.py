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

from weight_datanet import WeightTinySoft
from market_datanet import MarketTinySoft

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
        for item in result_array:
            database_obj.insert_data(item, table_name)

        tmp_successcount = getSusCount()

        info_str = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "Source: " + source +" Write " + str(len(result_array)) +" Items to Database, CurSuccessCount:  " + str(tmp_successcount) + " \n" 

        recordInfoWithLock(info_str)        
    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : \n" + exception_info
        recordInfoWithLock(info_str)  

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

def MultiThreadWriteData(data_type, ori_startdate, database_host=DATABASE_HOST):
    starttime = datetime.datetime.now()
    info_str = "+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
    LogInfo(g_logFile, info_str)   
    
    # data_type = "WeightData"
    database_name = data_type

    # ori_startdate = 20161101
    ori_enddate = getIntegerDateNow()

    database_obj = get_database_obj(database_name, host=database_host)
    netconn_obj = get_netconn_obj(data_type)

    source_array = netconn_obj.get_sourceinfo()
    tablename_array = source_array

    thread_count = 12

    database_obj.completeDatabaseTable(source_array)
    # database_obj.refreshDatabase(source_array)

    info_str = "Source Numb : " + str(len(source_array)) + '\n'
    LogInfo(g_logFile, info_str)   

    time_count = 0
    tmp_netdata_array = []
    tmp_source_array = []
    for i in range(len(source_array)):
        cur_source = source_array[i]
        cur_tablename = cur_source
        tabledata_startdate, tabledata_enddate = database_obj.getTableDataStartEndTime(cur_tablename)
        timeArray = netconn_obj.getStartEndTime(ori_startdate, ori_enddate, tabledata_startdate, tabledata_enddate)

        for j in range(len(timeArray)):
            startDate = timeArray[j][0]
            endDate = timeArray[j][1]
            ori_netdata = netconn_obj.get_netdata(cur_source, startDate, endDate)
            if ori_netdata is not None:
                time_count = time_count + 1 

                info_str = "[B] Source: " + str(cur_source) + ", from "+ str(startDate) +" to "+ str(endDate) \
                        + ", dataNumb: " + str(len(ori_netdata)) \
                        + ' , time_count: ' + str(time_count) + ", stockCount: "+ str(i+1) + "\n"
                LogInfo(g_logFile, info_str)  

                tmp_netdata_array.append(ori_netdata)
                tmp_source_array.append(cur_source)

                if (time_count % thread_count == 0) or (i == len(source_array)-1 and j == len(timeArray) -1):
                    # print ("tmp_netdata_array len: %d, tmpSecodeDataArray len: %d, i: %d") % (len(tmp_netdata_array), len(tmpSecodeDataArray), i)
                    startWriteThread(tmp_netdata_array, tmp_source_array, database_obj)
                    tmp_netdata_array = []
                    tmp_source_array = [] 
            else:
                info_str = "[C] Source: " + str(cur_source) + " has no data beteen "+ str(startDate) +" and "+ str(endDate) + " \n"
                LogInfo(g_logFile, info_str) 
        
        if len(timeArray) == 0:
                info_str = "[C] source: " + str(cur_source) + " already has data beteen "+ str(ori_startdate) +" and "+ str(ori_enddate) + " \n"
                LogInfo(g_logFile, info_str)

    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    aveTime = costTime / len(source_array)

    info_str = "++++++++++ End Time: " + str(endtime) \
            + " SumCostTime: " + str(costTime) + " AveCostTime: " + str(aveTime) + "s ++++++++\n"
    LogInfo(g_logFile, info_str)

def MultiThreadWriteIndustryData(data_type, ori_startdate, database_host=DATABASE_HOST):
    starttime = datetime.datetime.now()
    info_str = "+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
    LogInfo(g_logFile, info_str)   
    
    # data_type = "WeightData"
    database_name = data_type

    # ori_startdate = 20161101
    ori_enddate = getIntegerDateNow()

    database_obj = get_database_obj(database_name, host=database_host)
    netconn_obj = get_netconn_obj(data_type)

    source_array = netconn_obj.get_sourceinfo()
    tablename_array = source_array

    thread_count = 12

    database_obj.completeDatabaseTable(source_array)
    # database_obj.refreshDatabase(source_array)

    info_str = "Source Numb : " + str(len(source_array)) + '\n'
    LogInfo(g_logFile, info_str)   

    time_count = 0
    tmp_netdata_array = []
    tmp_source_array = []    

if __name__ == "__main__":
    data_type = "MarketDataTest"
    ori_startdate = 20171006    
    try:
        MultiThreadWriteData(data_type, ori_startdate)
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
            MultiThreadWriteData(data_type, ori_startdate)
