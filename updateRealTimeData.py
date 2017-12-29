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
    databaseobj.completeDatabaseTable([tableName])
    colname = "股票"
    for secode in secode_list):
        if databaseobj.check_data(colname, secode, table_name):
            databaseobj.update_data(nedata_array[secode], table_name)
        else:
            databaseobj.insert_data(nedata_array[secode], table_name)


def getSnapData(windObj, secodelist):
    ori_data = windObj.get_snapshoot_data(secodelist)

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

    for i in range(len(trans_data)):
        print trans_data[i]
        print tablename_array[i]

    startWriteThread(trans_data, tablename_array)

    # timer = threading.Timer(timeInterval, getSnapData, [windObj, secodelist])
    # timer.start();

def main():
    windObj = Wind()
    secodelist = ["000001.SZ", "000002.SZ", "600000.SH", "600006.SH", "600007.SH", "600008.SH", \
                  "600009.SH", "600010.SH", "600011.SH" , "600012.SH", "600015.SH", "600016.SH", \
                  "600017.SH", "600018.SH", "600019.SH", "600020.SH", "600021.SH", "600022.SH"]
    global timeInterval, thread_count, dbname, dbhost

    dbname = "MarketData_RealTime"
    dbhost = "localhost"
    thread_count = 12
    timeInterval = 2.0

    database_obj = MarketRealTimeDatabase(db=dbname, host=dbhost)
    database_obj.clearDatabase()
    database_obj.completeDatabaseTable(secodelist)

    timer = threading.Timer(timeInterval, getSnapData, [windObj, secodelist])
    timer.start();

if __name__ == "__main__":
    try:
        main()
    except Exception as exp:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                 + "__main__ Failed" + "\n" \
                 + "[E] Exception : " + exception_info
        print info_str
