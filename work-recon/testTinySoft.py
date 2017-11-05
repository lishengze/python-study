# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime

from CONFIG import *
from toolFunc import *
from TinyConn import TinySoft

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')
g_writeLogLock = threading.Lock()

def test_getSecodeInfo():
    tinysoft_connect = TinySoft(g_logFile, g_writeLogLock)
    result = tinysoft_connect.getSecodeInfo()
    print result[1:10]
        
def test_get_stockdata():
    tinysoft_connect = TinySoft(g_logFile, g_writeLogLock)
    secode = "SH600000"
    start_date = 20171001
    end_date = 20171103
    result = tinysoft_connect.getStockData(secode, start_date, end_date)
    if result is None:
        print secode + ' has no data between ' + str(start_date) + ' and ' + str(end_date)
    else:
        print result[1]

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
    tinyConn = TinySoft()
    tinyConn.startConnect()
    tinyConn.closeConnect()

if __name__ == "__main__":
    try:
        # test_connect()
        # test_getSecodeInfo()
        test_multi_thread_connect()
        # test_get_stockdata()
    except Exception as exp:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                 + "__main__ Failed" + "\n" \
                 + "[E] Exception : " + exception_info
        LogInfo(g_logFile, info_str) 
