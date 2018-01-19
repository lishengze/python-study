# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import time
import multiprocessing 


from CONFIG import *
from toolFunc import *
from wind import Wind
from WindPy import *
from market_realtime_database import MarketRealTimeDatabase
from market_preclose_database import MarketPreCloseDatabase

from excel import EXCEL

def writeDataToDatabase(nedata_array, tablename_array, databaseobj, dbname = "MarketData_RealTime", dbhost = "192.168.211.165"):
    # databaseobj = MarketRealTimeDatabase(db=dbname, host=dbhost)
    # databaseobj.completeDatabaseTable(tablename_array)
    for secode in tablename_array:
        databaseobj.insert_data(nedata_array[secode], secode)

def startProcess(netdata_array, tablename_array, database_obj_array, dbname = "MarketData_RealTime", dbhost = "192.168.211.165"):
    process_list = []
    for i in range(len(netdata_array)):
        tmp_process = multiprocessing.Process(target=writeDataToDatabase, \
                                              args=(netdata_array[i], tablename_array[i], database_obj_array[i], dbname, dbhost,))
        process_list.append(tmp_process)

    for process in process_list:
        process.start()

    for process in process_list:
        process.join()     

def startWriteThread(netdata_array, tablename_array, database_obj_array, dbname = "MarketData_RealTime", dbhost = "192.168.211.165"):
    threads = []
    for i in range(len(netdata_array)):
        tmp_thread = threading.Thread(target=writeDataToDatabase, \
                                      args=(netdata_array[i], tablename_array[i], database_obj_array[i], dbname, dbhost,))
        threads.append(tmp_thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()      

def writeRealTimeDataToOneChart(nedata_array, secodelist, table_name):
    databaseobj = MarketRealTimeDatabase(db=dbname, host=dbhost)
    databaseobj.completeDatabaseTable([table_name])
    update_numb = 0
    insert_numb = 0
    colname = "股票"
    for secode in secodelist:
        if databaseobj.check_data(colname, secode, table_name):            
            if len(nedata_array[secode]) == 6: 
                update_numb += 1
                databaseobj.update_data(nedata_array[secode], table_name)
        else:
            if len(nedata_array[secode]) == 6: 
                insert_numb += 1            
                databaseobj.insert_data(nedata_array[secode], table_name)

    print "update_realtime_numb: ", update_numb       
    print "insert_realtime_numb: ", insert_numb     

def allocate_threaddata(ori_data, secodelist):
    global thread_count
    tablename_array = secodelist
    trans_data = []
    tablename_array = []

    for j in range(thread_count):
        trans_data.append({})
        tablename_array.append([])

    i = 0
    while i < len(secodelist):           
        j = 0
        while j < thread_count and i + j < len(secodelist):
            secode = secodelist[i + j]
            trans_data[j][secode] = ori_data[secode]
            tablename_array[j].append(secode)
            j+=1
        i += thread_count

    return trans_data, tablename_array

def setSnapData(secodelist, database_obj_array):
    global windObj, struct_type, dbname, dbhost
    # print_data("database_obj_array: ", database_obj_array)

    ori_data = windObj.get_snapshoot_data(secodelist)
    print "ori_data.numb: ", len(ori_data)

    if g_IsWriteToOneChart:
        table_name = "AllData"
        writeRealTimeDataToOneChart(ori_data, secodelist, table_name)
    else:
        trans_data, tablename_array = allocate_threaddata(ori_data, secodelist)
        if struct_type == "Process":
            startProcess(trans_data, tablename_array, database_obj_array, dbname, dbhost)
        if struct_type == "Thread":
            startWriteThread(trans_data, tablename_array, database_obj_array, dbname, dbhost)

def setPreCloseData(secodelist, databaseobj):
    global windObj, dbhost, dbname
    result = windObj.get_preclose_data(secodelist)    
    # print result
    table_name = "PreCloseData"

    # databaseobj = MarketPreCloseDatabase(host=dbhost, db=dbname)
    databaseobj.completeDatabaseTable([table_name])

    colname = "股票"
    update_numb = 0
    insert_numb = 0
    for secode in secodelist:
        if databaseobj.check_data(colname, secode, table_name):            
            if len(result[secode]) == 2: 
                update_numb += 1
                databaseobj.update_data(result[secode], table_name)
        else:
            if len(result[secode]) == 2: 
                insert_numb += 1            
                databaseobj.insert_data(result[secode], table_name)

    print "update_preclose_numb: ", update_numb       
    print "insert_preclose_numb: ", insert_numb     

def scan_excelfile(database_obj_array):
    global secodelist, dirname, update_time

    if isTradingOver():
        return

    try:
        filename_array = get_filename_array(dirname)    
        newFileIn = False
        for filename in filename_array:
            complete_filename = dirname + '/' + filename
            excelobj = EXCEL(complete_filename)
            tmp_secodelist = excelobj.get_data_byindex()
            for code in tmp_secodelist:
                transcode = trans_code_to_windstyle(code)
                if transcode not in secodelist:
                    newFileIn = True
                    secodelist.append(transcode)                        
        print "secodenumb: ", len(secodelist) , ", newFileIn: ", newFileIn
        
        if newFileIn == True:
            database_obj_array[0].completeDatabaseTable(secodelist)
            setPreCloseData(secodelist, database_obj_array[len(database_obj_array)-1])

        if isTradingStart() and not isTradingRest():
            setSnapData(secodelist, database_obj_array)

    except Exception as e:
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "__Main__ Failed: \n" + "[E] Exception : \n" + exception_info
        print info_str

        get_snapshoot_data_error = "Get SnapShoot Data Failed"  
        get_preclose_data_error = "Get PreCLose Data Failed"
        excel_error = "Permission denied"

        isWindError = False
        isExcelError = False
        if get_snapshoot_data_error in exception_info:
            isWindError = True
        
        if get_preclose_data_error in exception_info:
            isWindError = True
            newFileIn = False

        if excel_error in exception_info:
            isExcelError = True

        if not isWindError or not isExcelError:
            raise(e)
    finally:
        timer = threading.Timer(update_time, scan_excelfile, args=(database_obj_array,))
        timer.start()

def set_secodelist(database_obj_array):
    global secodelist, dirname, update_time
    # dirname =  "D:/strategy"
    dirname = u"//192.168.211.182/1分钟数据 20160910-20170910/strategy"
    secodelist = get_indexcode(style="wind")

    timer = threading.Timer(update_time, scan_excelfile, args=(database_obj_array,))
    timer.start();

def main():
    global g_IsWriteToOneChart, update_time, thread_count, secodelist, struct_type
    global dbname, dbhost, windObj, g_testUpdate, g_testInsert

    # struct_type = "Process"
    struct_type = "Thread"
    secodelist = []
    dbname = "MarketData_RealTime"
    # dbhost = "localhost"
    dbhost = "192.168.211.165"
    thread_count = 12
    update_time = 3.0
    g_IsWriteToOneChart = False

    g_testUpdate = 0
    g_testInsert = 0

    database_obj_array = []
    for i in range(thread_count):
        database_obj = MarketRealTimeDatabase(db=dbname, host=dbhost)
        database_obj_array.append(database_obj)

    preclose_database_obj = MarketPreCloseDatabase(host=dbhost, db=dbname)
    database_obj_array.append(preclose_database_obj)

    windObj = Wind()
    set_secodelist(database_obj_array)

    database_obj = MarketRealTimeDatabase(db=dbname, host=dbhost)
    # database_obj.clearDatabase()

    if not isTradingStart():
        database_obj.clearDatabase()

    # database_obj.completeDatabaseTable(secodelist)

    # secodelist = ["000001.SZ", "000002.SZ", "600000.SH", "600006.SH", "600007.SH", "600008.SH", \
    #               "600009.SH", "600010.SH", "600011.SH" , "600012.SH", "600015.SH", "600016.SH", \
    #               "600017.SH", "600018.SH", "600019.SH", "600020.SH", "600021.SH", "600022.SH"]

    # secodelist = ["000001.SZ"]                  
    # setSnapData(secodelist)

    # timer = threading.Timer(timeInterval, setSnapData, [windObj,])
    # timer.start();

if __name__ == "__main__":
    main()
