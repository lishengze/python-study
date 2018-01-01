# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import time

from CONFIG import *
from toolFunc import *
from wind import Wind
from WindPy import *
from market_realtime_database import MarketRealTimeDatabase
from excel import EXCEL

def writeDataToDatabase(nedata_array, tablename_array):
    databaseobj = MarketRealTimeDatabase(db=dbname, host=dbhost)
    databaseobj.completeDatabaseTable(tablename_array)
    for secode in tablename_array:
        databaseobj.insert_data(nedata_array[secode], secode)

def startWriteThread(netdata_array, tablename_array):
    threads = []
    for i in range(len(netdata_array)):
        tmp_thread = threading.Thread(target=writeDataToDatabase, args=(netdata_array[i], tablename_array[i],))
        threads.append(tmp_thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()      
    
    print ("threading.active_count(): %d\n") % (threading.active_count())

def writeDataToOneChart(nedata_array, secode_list, table_name):
    databaseobj = MarketRealTimeDatabase(db=dbname, host=dbhost)
    databaseobj.completeDatabaseTable([table_name])
    update_numb = 0
    insert_numb = 0
    colname = "股票"
    for secode in secode_list:
        if databaseobj.check_data(colname, secode, table_name):            
            if len(nedata_array[secode]) == 6: 
                update_numb += 1
                databaseobj.update_data(nedata_array[secode], table_name)
        else:
            if len(nedata_array[secode]) == 6: 
                insert_numb += 1            
                databaseobj.insert_data(nedata_array[secode], table_name)

    print "update_numb: ", update_numb       
    print "insert_numb: ", insert_numb     

def allocate_threaddata(ori_data, secodelist):
    tablename_array = secodelist
    trans_data = []
    tablename_array = []

    for j in range(thread_count):
        trans_data.append({})
        tablename_array.append([])

    i = 0
    while i < len(secodelist, secodelist):           
        j = 0
        while j < thread_count and i + j < len(secodelist):
            secode = secodelist[i + j]
            trans_data[j][secode] = ori_data[secode]
            tablename_array[j].append(secode)
            j+=1
        i += thread_count

    for i in range(len(trans_data)):
        print trans_data[i]
        print tablename_array[i]    

    return trans_data, tablename_array

def getSnapData(secodelist):
    global windObj
    
    ori_data = windObj.get_snapshoot_data(secodelist)

    if g_IsWriteToOneChart:
        table_name = "AllData"
        writeDataToOneChart(ori_data, secodelist, table_name)
    else:
        trans_data, tablename_array = allocate_threaddata(ori_data, secodelist)
        startWriteThread(trans_data, tablename_array)

def scan_excelfile():
    global secodelist, dirname, update_time
    filename_array = get_filename_array(dirname)
    
    for filename in filename_array:
        complete_filename = dirname + '/' + filename
        excelobj = EXCEL(complete_filename)
        tmp_secodelist = excelobj.get_data_byindex()
        for code in tmp_secodelist:
            transcode = trans_code_to_windstyle(code)
            if transcode not in secodelist:
                secodelist.append(transcode)
                    
    print "secodenumb: ", len(secodelist)

    getSnapData(secodelist)

    timer = threading.Timer(update_time, scan_excelfile, )
    timer.start();

def set_secodelist():
    global secodelist, dirname, update_time
    dirname =  "D:/strategy"
    # secodelist = get_indexcode(style="wind")

    timer = threading.Timer(update_time, scan_excelfile, )
    timer.start();

def main():
    global g_IsWriteToOneChart, update_time, thread_count, secodelist
    global dbname, dbhost, windObj, g_testUpdate, g_testInsert

    secodelist = []
    dbname = "MarketData_RealTime"
    dbhost = "localhost"
    thread_count = 12
    update_time = 3.0
    g_IsWriteToOneChart = True

    g_testUpdate = 0;
    g_testInsert = 0;

    windObj = Wind()
    # set_secodelist()

    database_obj = MarketRealTimeDatabase(db=dbname, host=dbhost)
    database_obj.clearDatabase()
    # database_obj.completeDatabaseTable(secodelist)

    # secodelist = ["000001.SZ", "000002.SZ", "600000.SH", "600006.SH", "600007.SH", "600008.SH", \
    #               "600009.SH", "600010.SH", "600011.SH" , "600012.SH", "600015.SH", "600016.SH", \
    #               "600017.SH", "600018.SH", "600019.SH", "600020.SH", "600021.SH", "600022.SH"]

    secodelist = ["000001.SZ"]                  
    getSnapData(secodelist)

    # timer = threading.Timer(timeInterval, getSnapData, [windObj,])
    # timer.start();

if __name__ == "__main__":
    main()
