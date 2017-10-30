# -*- coding: UTF-8 -*-
import time
import pickle
import xlrd

import os, sys
import traceback
import pyodbc

from multiprocessing import cpu_count
import datetime
import threading

from example import MSSQL
from toolFunc import *
from CONFIG import *
from testFunc import *

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
            insertStr = getInsertStockDataStr(result[i], desTableName)
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
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)  

# 主线程必须在已创建的子线程执行完后，才能再创建新的子线程.
def startWriteThread(thread_count, databaseName, resultArray, secodeArray):
    try:
        threads = []
        for i in range(thread_count):
            tmpThread = threading.Thread(target=writeDataToDatabase, args=(resultArray[i], databaseName, str(secodeArray[i]), g_logFile))
            threads.append(tmpThread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()      
        
        print ("threading.active_count(): %d") % (threading.active_count())

    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "\n[X]: MainThread StartWriteThread Failed \n" \
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)           

def MultiThreadWriteData():
    try:
        starttime = datetime.datetime.now()
        infoStr = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
        LogInfo(g_logFile, infoStr)   

        thread_count = 8
        databaseName = "TestData"
        startDate = "20130901"
        endDate = "20170901"
        tmpMarketDataArray = []        
        tmpSecodeDataArray = []
        secodeArray = getSecodeInfoFromTianRuan(g_logFile)

        infoStr = "Secode Numb : " + str(len(secodeArray))
        LogInfo(g_logFile, infoStr)   

        secodeArray = secodeArray[0:thread_count*2]
        print secodeArray

        refreshTestDatabase(databaseName, secodeArray, g_logFile)

        for i in range(len(secodeArray)):


            stockHistMarketData = getStockData(secodeArray[i], startDate, endDate, g_logFile);
            # print("stockHistMarketData numb: %d") % (len(stockHistMarketData))

            tmpMarketDataArray.append(stockHistMarketData)
            tmpSecodeDataArray.append(secodeArray[i])

            if ((i+1) % thread_count == 0 and i != 0) or i == len(secodeArray)-1:
                # print ("tmpMarketDataArray len: %d, tmpSecodeDataArray len: %d, i: %d") % (len(tmpMarketDataArray), len(tmpSecodeDataArray), i)
                startWriteThread(thread_count, databaseName, tmpMarketDataArray, tmpSecodeDataArray)
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
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)   

if __name__ == "__main__":
    MultiThreadWriteData()
