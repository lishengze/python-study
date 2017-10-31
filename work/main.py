# -*- coding: UTF-8 -*-
import time

import os, sys
import traceback
import pyodbc

import datetime
import threading

from databaseClass import MSSQL
from CONFIG import *
from toolFunc import *
from databaseFunc import *
from netdataFunc import *

g_writeLogLock = threading.Lock()
g_susCount = 0
g_susCountLock = threading.Lock()
g_logFileName = os.getcwd() + '\log.txt'
g_logFile = open(g_logFileName, 'w')

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

def writeDataToDatabase(result, databaseName, secode, logFile):
    try:
        databaseObj = MSSQL() 
        tableName = secode
        desTableName = "["+ databaseName +"].[dbo].[" + tableName + "]"
        for i in range(len(result)):
            insertStr = getInsertStockDataStr(result[i], desTableName, g_logFile)
            insertRst = databaseObj.ExecStoreProduce(insertStr)

        tmpSuccessCount = getSusCount()

        infoStr = "[I] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "Stock: " + secode +" Write " + str(len(result)) +" Items to Database, CurSuccessCount:  " + str(tmpSuccessCount) + " \n" 

        databaseObj.CloseConnect()
        recordInfoWithLock(infoStr)        
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                + "writeDataToDatabase Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        # recordInfoWithLock(infoStr)  
        raise(Exception(infoStr))

def startWriteThread(databaseName, resultArray, secodeArray):
    try:
        threads = []
        for i in range(len(resultArray)):
            tmpThread = threading.Thread(target=writeDataToDatabase, args=(resultArray[i], databaseName, str(secodeArray[i]), g_logFile))
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
    try:
        starttime = datetime.datetime.now()
        infoStr = "+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
        LogInfo(g_logFile, infoStr)   

        thread_count = 12
        databaseName = "MarketData"
        oriStartDate = 20170930
        oriEndDate = getIntegerDateNow(g_logFile)

        tmpMarketDataArray = []        
        tmpSecodeDataArray = []
        secodeArray = getSecodeInfoFromTianRuan(g_logFile)

        infoStr = "Secode Numb : " + str(len(secodeArray)) + '\n'
        LogInfo(g_logFile, infoStr)   

        secodeArray = secodeArray[0:thread_count*2]
        print secodeArray

        completeDatabaseTable(databaseName, secodeArray, g_logFile)

        timeCount = 0
        for i in range(len(secodeArray)):
            curSecode = secodeArray[i]
            timeArray = getStartEndTime(oriStartDate, oriEndDate, databaseName, curSecode, g_logFile)
            for j in range(len(timeArray)):     
                startDate = timeArray[j][0]
                endDate = timeArray[j][1]             

                stockHistMarketData = getStockData(curSecode, startDate, endDate, g_logFile); 
                if stockHistMarketData is not None:
                    timeCount = timeCount + 1 

                    infoStr =  "[B] Stock: " + str(curSecode) + ", from "+ str(startDate) +" to "+ str(endDate) + ", dataNumb: " + str(len(stockHistMarketData)) + '\n'
                    LogInfo(g_logFile, infoStr)  

                    tmpMarketDataArray.append(stockHistMarketData)
                    tmpSecodeDataArray.append(curSecode)

                    if (timeCount % thread_count == 0) or (i == len(secodeArray)-1 and j == len(timeArray) -1):
                        # print ("tmpMarketDataArray len: %d, tmpSecodeDataArray len: %d, i: %d") % (len(tmpMarketDataArray), len(tmpSecodeDataArray), i)
                        startWriteThread(databaseName, tmpMarketDataArray, tmpSecodeDataArray)
                        tmpMarketDataArray = []
                        tmpSecodeDataArray = [] 
                    
        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        aveTime = deletaTime.seconds / len(secodeArray)

        infoStr = "++++++++++ End Time: " + str(endtime) \
                + " SumCostTime: " + str(deletaTime.seconds) + " AveCostTime: " + str(aveTime) + "s ++++++++\n"  
        LogInfo(g_logFile, infoStr)  

    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "\n" \
                +  "MultiThreadWriteData Failed" \
                + "[E] Exception : \n" + exceptionInfo
        # recordInfoWithLock(infoStr)  
        raise(Exception(infoStr)) 

if __name__ == "__main__":
    try:
        MultiThreadWriteData()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "__Main__ Failed" \
                + "[E] Exception : \n" + exceptionInfo
        recordInfoWithLock(infoStr)  
        raise(Exception(infoStr)) 
    
