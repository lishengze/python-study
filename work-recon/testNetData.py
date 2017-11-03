# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime

from CONFIG import *
from databaseClass import MSSQL
from toolFunc import *
from databaseFunc import *
from netdataFunc import *

g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')

def testGetSecodeInfo():
    secodeInfo = getSecodeInfoFromTianRuan(g_logFile)

    print len(secodeInfo[0])
    print type (secodeInfo[0])
    secode = str(secodeInfo[1][0])
    print secode[0:2], secode[2:]

def testGetStockData():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        code = 'SH600023'
        startDate = "20131030" 
        endDate = "20131218"
        tslStr = getMarketDataTslStr(code, startDate, endDate, g_logFile);
        curs.execute(tslStr)
        result = curs.fetchall()
        print len(result)
        print result[0][0] == -1
        curs.close()
        conn.close()
        return result        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "TestGetStockData Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        # LogInfo(g_logFile, infoStr)     
        raise(Exception(infoStr)) 

def testMultiThreadConnect():
    try:
        thread_count = 2
        threads = []

        for i in range(thread_count):

            tmpThread = threading.Thread(target=simpleConnect, args=(g_logFile,))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  \n" \
                + "TestMultiThread Failed" + "\n" \
                + "[E] Exception : \n" + exceptionInfo
        # LogInfo(g_logFile, infoStr) 
        raise(infoStr)        

def testGetAllStockDataCostDays():
    getAllStockDataCostDays(28, g_logFile)

def testGetStockGoMarkerTime():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        result = getStockGoMarkerTime(curs, '', g_logFile)
        curs.close()
        conn.close()
        return result
        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        exceptionInfo.decode('unicode_escape')
        LogInfo(g_logFile, exceptionInfo)  
        raise(infoStr)