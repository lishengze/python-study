# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime

from CONFIG import *
from toolFunc import *

from wind import Wind
from tinysoft import TinySoft
from database import Database

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')
g_writeLogLock = threading.Lock()

def compare_secodeinfo():
    wind_obj = Wind(g_logFileName, g_writeLogLock)
    tiny_obj = TinySoft(g_logFile, g_writeLogLock)
    wind_secodeinfo = wind_obj.getSecodeInfo()
    tiny_secodeinfo = tiny_obj.getSecodeInfo()

    data_onlyin_tiny = []
    data_onlyin_wind = []
    
    for secode in wind_secodeinfo:
        if secode not in tiny_secodeinfo:
            data_onlyin_wind.append(secode)

    print 'Data only in Wind: '
    print data_onlyin_wind

    for secode in tiny_secodeinfo:
        if secode not in wind_secodeinfo:
            data_onlyin_tiny.append(secode)
    print 'Data only in TinySoft'
    print data_onlyin_tiny

def compare_wind_database_secode(wind_secode, database_secode):
    """
    比较数据库中的证券代码集合与万得数据库中的证券代码集合。
    数据库中的证券代码集合应该是万得数据库中的证券代码集合的子集。
    """
    cmp_result = []
    for secode in database_secode:
        if secode not in wind_secode:
            cmp_result.append(secode)
    return cmp_result

def get_randon_subset(sumnumb, subnumb):
    result = []
    return result

def compare_databasedata_winddata(database_data, wind_data):
    return True
    
def getWindStartTime(database_stockdata):
    return []

def compare_data():
    """
    随机选择n支股票，每只股票选择m组数据进行比对
    """
    stock_numb = 100
    stock_data_numb = 1000
    database_obj = Database()
    wind_obj = Wind(g_logFile, g_writeLogLock)

    database_name = "MarketData"
    database_secode = database_obj.getDatabaseTableInfo(database_name)
    wind_secode = wind_obj.getSecodeInfo()
    secode_cmp_result = compare_wind_database_secode(wind_secode, database_secode)
    diff_count = 0

    if (len(secode_cmp_result) == 0):
        random_seocde_array = get_randon_subset(len(database_secode), stock_numb)
        for secode in random_seocde_array:
            table_name = "["+ database_name +"].[dbo].[" + secode + "]"
            database_data = database_obj.getDataByTableName(table_name)
            random_result_array = get_randon_subset(len(database_data), stock_data_numb)

            for i in random_result_array:
                database_stockdata = database_data[i]
                start_time = getWindStartTime(database_stockdata)
                end_time = start_time
                wind_stockdata  = wind_obj.getStockData(secode, start_time, end_time)
                if not compare_databasedata_winddata(database_data, wind_stockdata):
                    diff_count += 1

        print ("diff_count: %d \n") % (diff_count)
    else:
        print secode_cmp_result
    

if __name__ == "__main__":
    try:
        # test_connect()
        compare_secodeinfo()
        # test_multi_thread_connect()
        # test_get_stockdata()
    except Exception as exp:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                 + "__main__ Failed" + "\n" \
                 + "[E] Exception : " + exception_info
        LogInfo(g_logFile, info_str) 
