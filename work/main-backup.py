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

g_writeLogLock = threading.Lock()
g_susCount = 0
g_susCountLock = threading.Lock()
g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')

def recordInfoWithLock(infoStr):    
    global g_writeLogLock, g_logFile
    g_writeLogLock.acquire()
    print infoStr
    g_logFile.write(infoStr + '\n')
    g_writeLogLock.release()      
'''
功能：将数据写入数据库
'''
def WriteToDataBaseFromTianRuan(databaseObj, desTableName, result, taskCount):
    try:
        global g_susCount, g_susCountLock    
        rowNumb = len(result) 
        for i in range(0, len(result)):
            insertStr = getInsertStockDataStr(result[i], desTableName)
            insertRst = databaseObj.ExecStoreProduce(insertStr)

        g_susCountLock.acquire()
        g_susCount = g_susCount + 1
        tmp_susCount = g_susCount
        g_susCountLock.release()

        infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "WriteToTable " + desTableName + " Success , TaskCount is :" + str(taskCount) \
                + " Success count is: " + str(tmp_susCount) + "\n"
        recordInfoWithLock(infoStr)             
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "Write to dataTable " + desTableName +" Failed \n" \
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)      


def WriteToDataBaseFromExcel(databaseObj, desTableName, result, taskCount):    
    try:
        global g_susCount, g_susCountLock
        rowNumb = result.nrows
        # infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " \
        #             + "Write to Table " + desTableName + " Start!\n"    
        # recordInfoWithLock(infoStr)                    
        for i in range(1, rowNumb):
            colStr = " (TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
            dateTimeStr = transExcelTimeToStr(result.cell_value(i, 2))
            TDATE = getSimpleDate(dateTimeStr)
            TIME = getSimpleTime(dateTimeStr)
            SECODE = str(result.cell_value(i, 0))[2:]
            TOPEN = result.cell_value(i, 4)
            TCLOSE = result.cell_value(i, 5)
            HIGH = result.cell_value(i, 6)
            LOW = result.cell_value(i, 7)
            VOTRUNOVER = result.cell_value(i, 8)
            VATRUNOVER = result.cell_value(i, 9)
            TYClOSE = result.cell_value(i, 11)
            PCTCHG = (TCLOSE - TYClOSE) / TYClOSE

            valStr = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                    + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                    + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG)  

            insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"

            databaseObj.ExecStoreProduce(insertStr)    

        g_susCountLock.acquire()
        g_susCount = g_susCount + 1
        tmp_susCount = g_susCount
        g_susCountLock.release()

        infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "WriteToTable " + desTableName + " Success , TaskCount is :" + str(taskCount) \
                + " Success count is: " + str(tmp_susCount) + "\n"
        recordInfoWithLock(infoStr) 
        
    except: 
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "Write to dataTable " + desTableName +" Failed \n" \
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)         

'''
从天软获取数据并写入到数据库中
'''
def WriteTianRuanData(secodeInfo):
    try:
        databaseObj = MSSQL()    
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        for i in range(0, len(secodeInfo)):        
            secode = secodeInfo[i][0]
            desTableName = '[HistData].[dbo].[LCY_STK_01MS_' + secode[0:2] +'_' + secodeInfo[2:] + "]"
            downLoadedDataStartTime, downLoadedDataEndTime = getDownloadedDataStartEndTime(desTableName)
            stockGoMarkertTime = getStockGoMarkerTime(curs, secode)
            curStartTime, curEndTime = getCurStartEndTime(stockGoMarkertTime, downLoadedDataStartTime, downLoadedDataEndTime, STARTDATE, ENDDATE)

            tslStr = getMarketDataTslStr(secode, curStartTime, curEndTime)
            curs.execute(tslStr)
            result = curs.fetchall()

            infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " \
                    + secode +" GetDataByTime Success! InfoCount = " + str(len(result))
            recordInfoWithLock(infoStr)

            WriteToDataBaseFromTianRuan(databaseObj, desTableName, result, i+1)            

        databaseObj.CloseConnect()
        curs.close()
        conn.close()
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) +  "  " + "GetDataByTime Failed " \
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)      
        
'''
从Execl获取数据并写入到数据库中
'''
def WriteExeclData(secodeInfo):
    try :
        databaseObj = MSSQL()    
        infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + " ThreadTaskCount = " + str(len(secodeInfo))
        recordInfoWithLock(infoStr) 
        for i in range(0, len(secodeInfo)):        
            symbol = str(secodeInfo[i][0])
            market = str(secodeInfo[i][1])
            security = symbol + market
            fileName = market + symbol + '.xlsx'
            dirName =  EXCELFILE_DIR
            completeFileName = dirName + "\\" + fileName
            tableName = '[LCY_STK_01MS_' + secodeInfo[i][1] +'_' + secodeInfo[i][0] + "]"
            wholeTableName = '[HistData].[dbo].'+ tableName

            # infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " + 'desTableName: ' + desTableName + ' \n' \
            #         + "[i] threadName: " + str(threading.currentThread().getName()) + "  " + 'completeFileName: ' + completeFileName + '\n'
            # recordInfoWithLock(infoStr)             

            bk = xlrd.open_workbook(completeFileName)
            result = bk.sheet_by_name("Sheet1")
            infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " \
                    + "GetDataFromExcel " + fileName + " Success! InfoCount = " + str(result.nrows-1)
            recordInfoWithLock(infoStr) 
            WriteToDataBaseFromExcel(databaseObj, wholeTableName, result, i+1)
    
        databaseObj.CloseConnect()    
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "GetDataFromExcel " + fileName +" Failed \n" \
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)      

'''
测试主线程传递数据给子线程的方式
'''
def testThreadTransData(info, srcName):
    print 'testThreadTransData'
    print 'srcName: %s'%(srcName)
    print type(info)
    print len(info)
    print len(info[0])
    print type(info[0])
    print info[0][1]
    print info[0][0]

'''
作用： 从数据源读取每个证券的历史数据并写入数据库
过程：1. 为每个线程申请一个读取数据库的类对象
     2. 循环遍历证券代码表，组合得到每只证券的代码和交易所代码，向数据源申请历史数据 
        --- 向数据源申请数据可能是线程独立的，需要用锁控制，防止并发访问造成错误
     3. 将获得数据写入数据库表中。
'''
def InsertData(secodeInfo, srcName):
    try:
        if srcName == 'TIANRUAN':
            WriteTianRuanData(secodeInfo)
        elif srcName == "Excel":
            WriteExeclData(secodeInfo)
        else:
            print 'UnResolved Src!'        
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "InsertDatra Failed \n" \
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)              

'''
功能： 单线程获取所有历史数据并插入到数据库中
'''
def GetHistDataSingleThread():
    starttime = datetime.datetime.now()
    infoStr = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++"
    recordInfoWithLock(infoStr)

    secodeInfo = GetSecodeInfoFromDataTable()
    secodeInfo = secodeInfo[0:5]
    srcName = "Excel"
    InsertData(secodeInfo, srcName)

    endtime = datetime.datetime.now()
    deletaTime = endtime - starttime
    aveCostTime = deletaTime.seconds / len(secodeInfo) 
    infoStr = "++++++++++ End Time: " + str(endtime) \
            + ' Sum Cost Time: ' + str(deletaTime.seconds)  + "s" \
            + " Ave Cost Time: " + str(aveCostTime) + "s ++++++++\n"      
    recordInfoWithLock(infoStr)

def getSecodeInfo(srcName):
    if srcName == "Excel":
        addedSecodeInfo, secodeInfo = getCompleteSecodeInfoByExcel(g_logFile, EXCELFILE_DIR)        
    if srcName == "TIANRUAN":
        secodeInfo = getSecodeInfoFromTianRuan(g_logFile);
    return secodeInfo;

'''
作用：获取所有证券的历史数据
过程：1. 从数据库获取证券的代码信息。
     2. 根据CPU的数目和证券数设置读写线程的个数。
     3. 将证券代码信息按照线程数均分给不同的线程。
'''
def GetHistDataMultiThread(srcName):
    try: 
        global g_susCount

        databaseTable = GetDatabaseTableInfo()
        secodeInfo = getSecodeInfo(srcName)
        addedTableNumb = addTableBySecodeInfo(secodeInfo, databaseTable)

        secodeInfo = secodeInfo[1:9]

        threadCount = 4
        numbInterval = len(secodeInfo) / threadCount    
        if len(secodeInfo) % threadCount != 0:
            threadCount = threadCount + 1

        infoStr = '\nSecodeInfo count:' + str(len(secodeInfo)) + ', numbInterval: ' + str(numbInterval) + ', threadCount:' + str(threadCount)
        recordInfoWithLock(infoStr)

        threads = []
        for i in range(0, threadCount):
            startIndex = i * numbInterval
            endIndex = min((i+1) * numbInterval, len(secodeInfo))        
            print (startIndex, endIndex)

            threadSecodeInfo = secodeInfo[startIndex:endIndex]
            tmp = threading.Thread(target = InsertData, args = (threadSecodeInfo, srcName,))
            threads.append(tmp)

        starttime = datetime.datetime.now()
        infoStr = "\n+++++++++ Start Time: " + str(starttime) + " +++++++++++\n"
        recordInfoWithLock(infoStr)

        for thread in threads:
            thread.start()        
        for thread in threads:
            thread.join()

        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        if g_susCount == 0:
            infoStr = "++++++++++ End Time: " + str(endtime) \
                    + ' Sum Cost Time: ' + str(deletaTime.seconds)  + "s ++++++++\n"  
        else:
            aveCostTime = deletaTime.seconds / g_susCount 
            infoStr = "++++++++++ End Time: " + str(endtime) \
                    + ' Sum Cost Time: ' + str(deletaTime.seconds)  + "s" \
                    + " Ave Cost Time: " + str(aveCostTime) + "s ++++++++\n"    
        recordInfoWithLock(infoStr)
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "GetHistDataMultiThread Failed \n" \
                + "[E] Exception : " + exceptionInfo
        recordInfoWithLock(infoStr)            

def GetDataFromTianRuan():
    srcName = "TIANRUAN"
    GetHistDataMultiThread(srcName)
    print "username: %s, password: %s" %(QT_USR, QT_PWD)

def GetDataFromExcel():
    srcName = "Excel"
    GetHistDataMultiThread(srcName)

if __name__ == "__main__":
    GetDataFromExcel()
