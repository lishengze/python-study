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

from TinyConn import TinySoft
from databaseClass import Database

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

def recordInfoWithLock(infoStr):
    global g_writeLogLock, g_logFile
    g_writeLogLock.acquire()
    print infoStr
    g_logFile.write(infoStr + '\n')
    g_writeLogLock.release()      

def writeDataToDatabase(result, databaseName, secode, tinysoftObj):
    try:
        databaseObj = Database()
        tableName = secode
        desTableName = "["+ databaseName +"].[dbo].[" + tableName + "]"
        for i in range(len(result)):
            insertStr = tinysoftObj.getInsertStockDataStr(result[i], desTableName)
            databaseObj.changeDatabase(insertStr)

        tmpSuccessCount = getSusCount()

        infoStr = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "Stock: " + secode +" Write " + str(len(result)) +" Items to Database, CurSuccessCount:  " + str(tmpSuccessCount) + " \n" 

        recordInfoWithLock(infoStr)        
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        recordInfoWithLock(infoStr)  

def startWriteThread(databaseName, resultArray, secodeArray, tinysoftObj):
    try:
        threads = []
        for i in range(len(resultArray)):
            tmpThread = threading.Thread(target=writeDataToDatabase, args=(resultArray[i], databaseName, str(secodeArray[i]), tinysoftObj,))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()      
        
        print ("threading.active_count(): %d\n") % (threading.active_count())

    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "\n[X]: MainThread StartWriteThread Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        # recordInfoWithLock(infoStr)       
        raise(Exception(infoStr))    

def MultiThreadWriteData():
    starttime = datetime.datetime.now()
    infoStr = "+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
    LogInfo(g_logFile, infoStr)   

    thread_count = 12
    databaseName = "MarketData"
    oriStartDate = 20171030
    oriEndDate = getIntegerDateNow()

    tinysoftObj = TinySoft(g_logFile, g_writeLogLock)
    databaseObj = Database()

    tmpMarketDataArray = []        
    tmpSecodeDataArray = []
    secodeArray = tinysoftObj.getSecodeInfo()

    infoStr = "Secode Numb : " + str(len(secodeArray)) + '\n'
    LogInfo(g_logFile, infoStr)   

    # secodeArray = secodeArray[0:thread_count*2]
    # print secodeArray

    # refreshDatabase(databaseName, secodeArray, g_logFile)
    # completeDatabaseTable(databaseName, secodeArray, g_logFile)
            
    databaseObj.completeDatabaseTable(databaseName, secodeArray)

    timeCount = 0
    for i in range(len(secodeArray)):
        curSecode = secodeArray[i]
        tableDataStartTime, tableDataEndTime = databaseObj.getTableDataStartEndTime(databaseName, curSecode)
        timeArray = tinysoftObj.getStartEndTime(oriStartDate, oriEndDate, tableDataStartTime, tableDataEndTime)
        for j in range(len(timeArray)):     
            startDate = timeArray[j][0]
            endDate = timeArray[j][1]             

            stockHistMarketData = tinysoftObj.getStockData(curSecode, startDate, endDate); 
            if stockHistMarketData is not None:
                timeCount = timeCount + 1 

                infoStr = "[B] Stock: " + str(curSecode) + ", from "+ str(startDate) +" to "+ str(endDate) \
                        + ", dataNumb: " + str(len(stockHistMarketData)) \
                        + ' , timeCount: ' + str(timeCount) + ", stockCount: "+ str(i+1) + "\n"
                LogInfo(g_logFile, infoStr)  

                tmpMarketDataArray.append(stockHistMarketData)
                tmpSecodeDataArray.append(curSecode)

                if (timeCount % thread_count == 0) or (i == len(secodeArray)-1 and j == len(timeArray) -1):
                    # print ("tmpMarketDataArray len: %d, tmpSecodeDataArray len: %d, i: %d") % (len(tmpMarketDataArray), len(tmpSecodeDataArray), i)
                    startWriteThread(databaseName, tmpMarketDataArray, tmpSecodeDataArray, tinysoftObj)
                    tmpMarketDataArray = []
                    tmpSecodeDataArray = [] 
            else:
                infoStr = "[C] Stock: " + str(curSecode) + " has no data beteen "+ str(startDate) +" and "+ str(endDate) + " \n"
                LogInfo(g_logFile, infoStr) 
        
        if len(timeArray) == 0:
                infoStr = "[C] Stock: " + str(curSecode) + " already has data beteen "+ str(oriStartDate) +" and "+ str(oriEndDate) + " \n"
                LogInfo(g_logFile, infoStr)                 
                
    endtime = datetime.datetime.now()
    costTime = (endtime - starttime).seconds
    aveTime = costTime / len(secodeArray)

    infoStr = "++++++++++ End Time: " + str(endtime) \
            + " SumCostTime: " + str(costTime) + " AveCostTime: " + str(aveTime) + "s ++++++++\n"  
    LogInfo(g_logFile, infoStr)  

if __name__ == "__main__":
    try:
        MultiThreadWriteData()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "__Main__ Failed" \
                + "[E] Exception : \n" + exceptionInfo
        recordInfoWithLock(infoStr)  

        # connFailedError = "Communication link failure---InternalConnect"
        # connFailedWaitTime = 60 * 5
        # if connFailedError in infoStr:
        #     time.sleep(connFailedWaitTime)
        #     infoStr = "[RS] MultiThreadWriteData  Restart : \n" 
        #     recordInfoWithLock(infoStr)  
        #     MultiThreadWriteData()
    
