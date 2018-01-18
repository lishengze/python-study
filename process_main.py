# -*- coding: UTF-8 -*-
import time

import os, sys
import traceback
import pyodbc

import datetime
import threading
import multiprocessing 

from CONFIG import *
from toolFunc import *

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

def get_database_obj(database_name, host='localhost', id=0):
    if "WeightData" in database_name:
        return WeightDatabase(host=host, db=database_name)

    if "MarketData" in database_name:
        return MarketDatabase(id=id, host=host, db=database_name)

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
    print info_str
    # global g_writeLogLock, g_logFile
    # g_writeLogLock.acquire()
    # print info_str
    # g_logFile.write(info_str + '\n')
    # g_writeLogLock.release()      

def writeDataToDatabase(result_array, source, database_obj):
    try:
        # database_obj = get_database_obj(mainthread_database_obj.db, mainthread_database_obj.host)        
        table_name = source
        # database_obj.completeDatabaseTable([table_name])        
        for item in result_array:
            database_obj.insert_data(item, table_name)
        # tmp_successcount = getSusCount()

        # info_str = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
        info_str = "[I] Source: " + source +" Write " + str(len(result_array)) +" Items to " + database_obj.db \
                + ", database id: "+ str(database_obj.id)  +"\n"
                # +", CurSuccessCount:  " + str(tmp_successcount) + " \n" 

        recordInfoWithLock(info_str)        
    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : \n" + exception_info
        recordInfoWithLock(info_str)  
        sleeptime = 30
        print "-------- writeDataToDatabase sleep: " + str(sleeptime) + " ----------"        
        time.sleep(sleeptime)
        print "[RS]: writeDataToDatabase restart!"
        writeDataToDatabase(result_array, source, mainthread_database_obj)

def writeDataToDatabaseProcess(result_array, source, database_obj_main):
    try:
        database_obj = get_database_obj(database_obj_main.db, database_obj_main.host)        
        table_name = source
        database_obj.completeDatabaseTable([table_name])        
        for item in result_array:
            database_obj.insert_data(item, table_name)
        # tmp_successcount = getSusCount()

        # info_str = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
        info_str = "[I] Source: " + source +" Write " + str(len(result_array)) +" Items to " + database_obj.db \
                + ", database id: "+ str(database_obj.id)  +"\n"
                # +", CurSuccessCount:  " + str(tmp_successcount) + " \n" 

        recordInfoWithLock(info_str)        
    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : \n" + exception_info
        recordInfoWithLock(info_str)  
        sleeptime = 30
        print "-------- writeDataToDatabase sleep: " + str(sleeptime) + " ----------"        
        time.sleep(sleeptime)
        print "[RS]: writeDataToDatabase restart!"
        writeDataToDatabase(result_array, source, mainthread_database_obj)

def startWriteThread(netdata_array, source_array, database_obj_array):
    threads = []
    for i in range(len(netdata_array)):
        tmp_thread = threading.Thread(target=writeDataToDatabase, args=(netdata_array[i], str(source_array[i]), database_obj_array[i],))
        threads.append(tmp_thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()      
    
    print ("threading.active_count(): %d\n") % (threading.active_count())

def startWriteProcess(netdata_array, source_array, database_obj):
    process_list = []
    for i in range(len(netdata_array)):
        tmp_process = multiprocessing.Process(target=writeDataToDatabase, args=(netdata_array[i], str(source_array[i]), database_obj,))
        process_list.append(tmp_process)

    for process in process_list:
        process.start()

    for process in process_list:
        process.join()     
    
    print ("threading.active_count(): %d\n") % (threading.active_count())

def MultiThreadWriteData(data_type, source_conditions, database_host=DATABASE_HOST):
    starttime = datetime.datetime.now()
    info_str = "+++++++++ "+ data_type +" Start Time: " + str(starttime) + " +++++++++++\n"
    LogInfo(g_logFile, info_str)

    database_name = data_type
    
    # struct_type = "process"
    struct_type = "thread"

    database_obj = get_database_obj(database_name, host=database_host)
    netconn_obj = get_netconn_obj(data_type)

    source = netconn_obj.get_sourceinfo(source_conditions)
    tablename_array = netconn_obj.get_tablename(source_conditions)

    source = database_obj.filter_source(source)
    tablename_array = database_obj.filter_tableArray(tablename_array)
    info_str = "Table Numb : " + str(len(tablename_array)) + '\n'
    LogInfo(g_logFile, info_str)

    database_obj.completeDatabaseTable(tablename_array)

    thread_count = 12
    database_obj_array = []
    for i in range(thread_count):
        tmp_database_obj = get_database_obj(database_name, host=database_host, id=i)
        database_obj_array.append(tmp_database_obj)

    condition_count = 0
    tmp_netdata_array = []
    tmp_tablename_array = []

    sus_secode = []
    restore_data = []
    restore_dict_data = {}

    if "MarketData" in data_type:
        com_tradetime_array = get_index_tradetime(netconn_obj, source_conditions[0], source_conditions[1])
        latest_data = database_obj.getAllLatestData(tablename_array)
        first_data = database_obj.getALLFirstData(tablename_array)

    for table_name in tablename_array:
        restore_dict_data[table_name] = []

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

                condition_count = condition_count + 1
                info_str = "[B] Source: " + str(cur_condition) + ", OriDataNumb: " + str(len(ori_netdata)) 
                if "MarketData" in data_type:                    
                    # Get Restore Info
                    cur_restore_data = get_restore_info(cur_tablename, ori_netdata, \
                                        latestdata = latest_data[cur_tablename], firstdata=first_data[cur_tablename])
                    if len(restore_dict_data[cur_tablename]) == 0 or (len(cur_restore_data) != 0 and \
                       is_time_late([restore_dict_data[cur_tablename][1], restore_dict_data[cur_tablename][2]], \
                                    [cur_restore_data[1], cur_restore_data[2]])):
                        restore_dict_data[cur_tablename] = cur_restore_data

                    #Complete Suspend Data
                    old_oridata_numb = len(ori_netdata)
                    tradetime_array = get_sub_index_tradetime(com_tradetime_array, cur_condition[1], cur_condition[2])
                    # print "Current: tradetime_array.size: ", len(tradetime_array)
                    complete_data = add_suspdata(tradetime_array, ori_netdata, isfirstInterval, latest_data[cur_tablename])
                    info_str += ", CompleteDataNumb: " + str(len(complete_data))
                    ori_netdata = complete_data
                    if len(complete_data) != old_oridata_numb:
                        sus_secode.append([cur_tablename, len(complete_data) - old_oridata_numb])
                
                tmp_netdata_array.append(ori_netdata)
                tmp_tablename_array.append(cur_tablename)

                if (condition_count % thread_count == 0) or (i == len(tablename_array)-1 and j == len(database_transed_conditions) -1):
                    if struct_type == "process":
                        startWriteProcess(tmp_netdata_array, tmp_tablename_array, database_obj)                    
                    if struct_type == "thread":
                        startWriteThread(tmp_netdata_array, tmp_tablename_array, database_obj_array)

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
    for secode in restore_dict_data:
        if len(restore_dict_data[secode]) != 0:
            restore_data.append(restore_dict_data[secode])

    print_data("restore_data: ", restore_data)
    info_str = "++++++++++"+ data_type +" End Time: " + str(endtime) \
            + " SumCostTime: " + str(costTime) + "s, AveCostTime: " + str(aveTime) + "s ++++++++\n"
    LogInfo(g_logFile, info_str)      
    return restore_data

def compareTimeData(ori_startdate=0, ori_enddate=0, data_type="MarketData_day", host = "localhost"):       
    database_obj = get_database_obj(data_type, host=host)
    netconn_obj = get_netconn_obj(data_type)

    trade_time_array = get_index_tradetime(netconn_obj,ori_startdate, ori_enddate)

    tablename_array = database_obj.getDatabaseTableInfo()
    right_Data = {}
    error_data = {}
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
                error_data[tablename] = curdata
            else:
                curdata.append("TRUE")
                right_Data[tablename] = curdata
    print_dict_data("error_sus_data: ", error_data)

def update_restore_data(mainthread_database_obj, restore_data):
    for item in restore_data:
        if len(item) == 0:
            continue
        secode = item[0]
        enddate = item[1]
        col_str = "[TDATE], [TIME], [TCLOSE], [PCTCHG], [YCLOSE]"
        database_obj = get_database_obj(mainthread_database_obj.db, mainthread_database_obj.host)
        ori_data = database_obj.get_histdata_by_enddate(enddate, secode, col_str)
        ori_data.sort(key=itemgetter(0,1))
        ori_data = compute_restore_data(ori_data)
        database_obj.update_restore_data(secode, ori_data)
        info_str = "[I] Source: " + secode +" Update " + str(len(ori_data)) +" Items to " + database_obj.db \
                 + ", procss id: "+ str(os.getpid())  +"\n"
        # recordInfoWithLock(info_str)   
    # ori_data = None
        
def restore_database(database_obj, restore_data, compute_count):   
    starttime = datetime.datetime.now()
    info_str = "********** Restore_database Start Time: " + str(starttime) + " **********\n"
    LogInfo(g_logFile, info_str)

    trans_restore_data = []
    if [] in restore_data:
        restore_data.remove([])
    for j in range(compute_count):
        trans_restore_data.append([])

    i = 0
    while i < len(restore_data):
        j = 0
        while j < compute_count and i + j < len(restore_data):
            trans_restore_data[j].append(restore_data[i+j])
            j += 1
        i += j

    if [] in trans_restore_data:
        trans_restore_data.remove([])
    # print_data("trans_restore_data: ", trans_restore_data)

    process_list = []
    for j in range(len(trans_restore_data)):
        if len(trans_restore_data[j]) != 0:
            tmp_process = multiprocessing.Process(target=update_restore_data, args=(database_obj, trans_restore_data[j],))
            process_list.append(tmp_process)

    # print_data("process_list: ", process_list)

    for process in process_list:
        process.start()

    for process in process_list:
        process.join()    

    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    info_str = "++++++++++ restore_database End Time: " + str(endtime) + " SumCostTime: " + str(float(costTime)/60.0) + " m"

    ave_costtime = -1
    if len(restore_data) != 0:
        ave_costtime = costTime / len(restore_data)
    if ave_costtime != -1:
        info_str += ", ave_costtime: " + str(ave_costtime) + "s "

    info_str += " **********\n"    
    LogInfo(g_logFile, info_str) 

def download_data():
    # data_type = "MarketDataTest"
    # data_type = "WeightDataTest"
    # data_type = "IndustryDataTest"
    data_type = "IndustryData"
    # data_type = "WeightData"
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
    # time_frequency = ["5m", "10m", "30m",  "week", "month"]
    time_frequency = ["30m"]
    host = "192.168.211.165"
    # host = "localhost"
    ori_startdate = 20130101
    # ori_enddate = 20170622

    for timeType in time_frequency:         
        data_type = "MarketData" + "_" + timeType
        ori_enddate = getDateNow(data_type)   

        database_obj = get_database_obj(data_type, host=host)
        database_obj.clearDatabase()

        restore_data = MultiThreadWriteData(data_type, [ori_startdate, ori_enddate], database_host=host)          
        compareTimeData(ori_startdate, ori_enddate, data_type, host)

        compute_count = 12
        restore_database(database_obj, restore_data, compute_count)

def main():
    starttime = datetime.datetime.now()
    info_str = "********** Main Start Time: " + str(starttime) + " **********\n"
    LogInfo(g_logFile, info_str)

    try:
        download_Marketdata()        
        # download_data()
    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "__Main__ Failed" + "[E] Exception : \n" + exception_info
        recordInfoWithLock(info_str)

        connFailedError = "Communication link failure---InternalConnect"
        driver_error = "The dirver did not supply an error"
        tiny_error = "self.curs.execute(tsl_str)"
        sql_error = "self.cur.execute(sql)"
        connFailedWaitTime = 30
        if connFailedError in info_str \
        or driver_error in info_str \
        or tiny_error in info_str \
        or sql_error in info_str:
            print "[RS] MultiThreadWriteData Sleep " + str(connFailedWaitTime) + "S"
            time.sleep(connFailedWaitTime)
            info_str = "[RS] MultiThreadWriteData  Restart : \n"
            recordInfoWithLock(info_str)
            main()

    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    info_str = "++++++++++ Main End Time: " + str(endtime) + " SumCostTime: " + str(costTime/60) + " m **********\n"
    LogInfo(g_logFile, info_str)     

if __name__ == "__main__":
    main()
 