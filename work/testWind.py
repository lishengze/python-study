# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime

from CONFIG import *
from toolFunc import *
from wind import Wind

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')
g_writeLogLock = threading.Lock()

def printpy(outdata):
    if outdata.ErrorCode!=0:
        print('error code:'+str(outdata.ErrorCode)+'\n');
        return();
    for i in range(0,len(outdata.Data[0])):
        strTemp=''
        if len(outdata.Times)>1:
            strTemp=str(outdata.Times[i])+' '
        for k in range(0, len(outdata.Fields)):
            strTemp=strTemp+str(outdata.Data[k][i])+' '
        print(strTemp)

def test_getSecodeInfo():
    tinysoft_connect = Wind(g_logFile, g_writeLogLock)
    result = tinysoft_connect.getSecodeInfo()
    print len(result)
    print result[1:10]
        
def test_get_stockdata():
    wind_connect = Wind(g_logFile, g_writeLogLock)
    secode = "600000.SH"
    start_date = '20171107 093100'
    end_date = '20171107 093200'
    result = wind_connect.getStockData(secode, start_date, end_date)
    if result is None:
        print secode + ' has no data between ' + str(start_date) + ' and ' + str(end_date)
    else:
        printpy(result)
        # print result[1]

def test_multi_thread_connect():
    thread_count = 2
    threads = []
    for i in range(thread_count):
        tmpThread = threading.Thread(target=Wind, args=(g_logFile, g_writeLogLock,))
        threads.append(tmpThread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()     

def test_connect():
    wind_obj = Wind(g_logFile, g_writeLogLock)

if __name__ == "__main__":
    try:
        # test_connect()
        # test_getSecodeInfo()
        # test_multi_thread_connect()
        test_get_stockdata()
    except Exception as exp:
        exception_info = '\n' + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                 + "__main__ Failed" + "\n" \
                 + "[E] Exception : " + exception_info
        LogInfo(g_logFile, info_str) 
