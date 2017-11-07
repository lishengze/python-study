# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime

from CONFIG import *
from toolFunc import *
from tinysoft import TinySoft
from database import Database

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')
g_writeLogLock = threading.Lock()

def test_getSecodeInfo():
    tinysoft_connect = TinySoft(g_logFile, g_writeLogLock)
    result = tinysoft_connect.getSecodeInfo()
    print len(result)
    # print result[1:10]
        
def test_get_stockdata():
    tinysoft_connect = TinySoft(g_logFile, g_writeLogLock)
    secode = "SH600000"
    start_date = 20171101
    end_date = 20171101
    result = tinysoft_connect.getStockData(secode, start_date, end_date)
    if result is None:
        print secode + ' has no data between ' + str(start_date) + ' and ' + str(end_date)
    else:
        print result[1:4]

def test_get_weight_data():
    tiny_obj = TinySoft(g_logFile, g_writeLogLock)
    secode_array = tiny_obj.getIndexSecode()
    start_date = 20171104
    end_date = 20171107 
    secode ="SH000016"
    result = tiny_obj.getWeightData(secode, start_date, end_date)
    # for secode in secode_array:
    #     result = tiny_obj.getWeightData(secode, start_date, end_date)
    #     print 'secode weight result len: ' + str(len(result))

def test_multi_thread_connect():
    try:
        thread_count = 2
        threads = []
        for i in range(thread_count):
            tmpThread = threading.Thread(target=TinySoft, args=(g_logFile, g_writeLogLock,))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                + "TestMultiThread Failed" + "\n" \
                + "[E] Exception : \n" + exception_info
        # LogInfo(g_logFile, info_str) 
        raise(info_str)        

def test_connect():
    tinyConn = TinySoft(g_logFile, g_writeLogLock)

def write_weightdata(database_obj, oridata, table_name):
    for oneday_data in oridata:
        for item in oneday_data:
            database_obj.insert_data(item, table_name)

def test_singlethread_write_weightdata():
    database_name = "WeightDataTest"
    start_date = 20171104
    end_date = 20171105

    database_obj = Database(db=database_name)
    tinysoft_obj = TinySoft(g_logFile, g_writeLogLock)
    secode_array = tinysoft_obj.getIndexSecode()
    database_obj.completeDatabaseTable(secode_array)

    for secode in secode_array:
        result = tinysoft_obj.getWeightData(secode, start_date, end_date)
        write_weightdata(database_obj, result, secode)

if __name__ == "__main__":
    try:
        # test_connect()
        # test_getSecodeInfo()
        # test_multi_thread_connect()
        # test_get_stockdata()
        # test_get_weight_data()
        test_singlethread_write_weightdata()
    except Exception as exp:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                 + "__main__ Failed" + "\n" \
                 + "[E] Exception : " + exception_info
        LogInfo(g_logFile, info_str) 
