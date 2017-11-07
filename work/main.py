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
from tinysoft import TinySoft
from database import Database

g_writeLogLock = threading.Lock()
g_logFileName = os.getcwd() + '\log.txt'
g_logFile = open(g_logFileName, 'w')
g_susCount = 0
g_susCountLock = threading.Lock()

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

def writeDataToDatabase(result, databaseName, secode, netConnObj):
    try:
        database_obj = Database()
        table_name = secode
        desTableName = "["+ databaseName +"].[dbo].[" + table_name + "]"
        for i in range(len(result)):
            insertStr = netConnObj.getInsertStockDataStr(result[i], desTableName)
            database_obj.changeDatabase(insertStr)

        tmpSuccessCount = getSusCount()

        info_str = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "Stock: " + secode +" Write " + str(len(result)) +" Items to Database, CurSuccessCount:  " + str(tmpSuccessCount) + " \n" 

        recordInfoWithLock(info_str)        
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        recordInfoWithLock(info_str)  

def startWriteThread(databaseName, resultArray, secodeArray, netConnObj):
    try:
        threads = []
        for i in range(len(resultArray)):
            tmpThread = threading.Thread(target=writeDataToDatabase, args=(resultArray[i], databaseName, str(secodeArray[i]), netConnObj,))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()      
        
        print ("threading.active_count(): %d\n") % (threading.active_count())

    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "\n[X]: MainThread StartWriteThread Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        # recordInfoWithLock(info_str)       
        raise(Exception(info_str))    

def MultiThreadWriteData():
    starttime = datetime.datetime.now()
    info_str = "+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
    LogInfo(g_logFile, info_str)   

    thread_count = 12
    databaseName = "MarketData"
    oriStartDate = 20171101
    oriEndDate = getIntegerDateNow()

    tinySoftObj = TinySoft(g_logFile, g_writeLogLock)
    netConnObj = tinySoftObj

    databaseServer = "localhost"
    database_obj = Database(host=databaseServer)

    tmpMarketDataArray = []        
    tmpSecodeDataArray = []
    secodeArray = netConnObj.getSecodeInfo()

    info_str = "Secode Numb : " + str(len(secodeArray)) + '\n'
    LogInfo(g_logFile, info_str)   

    secodeArray = secodeArray[0:thread_count*2]
    # print secodeArray

    database_obj.refreshDatabase(secodeArray)
    # database_obj.completeDatabaseTable(secodeArray)

    timeCount = 0
    for i in range(len(secodeArray)):
        curSecode = secodeArray[i]
        tableDataStartTime, tableDataEndTime = database_obj.getTableDataStartEndTime(curSecode)
        timeArray = netConnObj.getStartEndTime(oriStartDate, oriEndDate, tableDataStartTime, tableDataEndTime)
        for j in range(len(timeArray)):     
            startDate = timeArray[j][0]
            endDate = timeArray[j][1]             

            stockHistMarketData = netConnObj.getStockData(curSecode, startDate, endDate)
            if stockHistMarketData is not None:
                timeCount = timeCount + 1 

                info_str = "[B] Stock: " + str(curSecode) + ", from "+ str(startDate) +" to "+ str(endDate) \
                        + ", dataNumb: " + str(len(stockHistMarketData)) \
                        + ' , timeCount: ' + str(timeCount) + ", stockCount: "+ str(i+1) + "\n"
                LogInfo(g_logFile, info_str)  

                tmpMarketDataArray.append(stockHistMarketData)
                tmpSecodeDataArray.append(curSecode)

                if (timeCount % thread_count == 0) or (i == len(secodeArray)-1 and j == len(timeArray) -1):
                    # print ("tmpMarketDataArray len: %d, tmpSecodeDataArray len: %d, i: %d") % (len(tmpMarketDataArray), len(tmpSecodeDataArray), i)
                    startWriteThread(databaseName, tmpMarketDataArray, tmpSecodeDataArray, netConnObj)
                    tmpMarketDataArray = []
                    tmpSecodeDataArray = [] 
            else:
                info_str = "[C] Stock: " + str(curSecode) + " has no data beteen "+ str(startDate) +" and "+ str(endDate) + " \n"
                LogInfo(g_logFile, info_str) 
        
        if len(timeArray) == 0:
                info_str = "[C] Stock: " + str(curSecode) + " already has data beteen "+ str(oriStartDate) +" and "+ str(oriEndDate) + " \n"
                LogInfo(g_logFile, info_str)
    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    aveTime = costTime / len(secodeArray)

    info_str = "++++++++++ End Time: " + str(endtime) \
            + " SumCostTime: " + str(costTime) + " AveCostTime: " + str(aveTime) + "s ++++++++\n"
    LogInfo(g_logFile, info_str)

if __name__ == "__main__":
    try:
        MultiThreadWriteData()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "__Main__ Failed" \
                + "[E] Exception : \n" + exceptionInfo
        recordInfoWithLock(info_str)
        connFailedError = "Communication link failure---InternalConnect"
        connFailedWaitTime = 60 * 5
        if connFailedError in info_str:
            time.sleep(connFailedWaitTime)
            info_str = "[RS] MultiThreadWriteData  Restart : \n"
            recordInfoWithLock(info_str)
            MultiThreadWriteData()
