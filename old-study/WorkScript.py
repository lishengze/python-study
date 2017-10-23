# -*- coding: UTF-8 -*-
import time
import pickle
import xlrd
from QtAPI import *
from QtDataAPI import *
from example import MSSQL
from TestApi import TestApi
# from toolFunc import getSimpleDate, getSimpleTime, transExcelTimeToStr, getSecodeInfo, GetSecodeInfo
from toolFunc import *

import os, sys
import traceback

from multiprocessing import cpu_count
import datetime
import threading

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
def WriteToDataBaseFromNet(databaseObj, desTableName, result, taskCount):
    try:
        global g_susCount, g_susCountLock    
        rowNumb = len(result) 
        for i in range(0, len(result)):
            colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
            valStr = getSimpleDate(result.iloc[i, 0]) + ", " + getSimpleTime(result.iloc[i, 1]) + ", \'"+ result.iloc[i, 2] + "\'," \
                    + str(result.iloc[i, 3]) + ", " + str(result.iloc[i, 4]) + ", " + str(result.iloc[i, 5]) + ", " \
                    + str(result.iloc[i, 6]) + ", " + str(result.iloc[i, 7]) + ", " + str(result.iloc[i, 8]) + ", " \
                    + str(result.iloc[i, 9])   

            insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
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
从网络接口获取数据并写入到数据库中
'''
def WriteNetData(secodeInfo):
    try:
        databaseObj = MSSQL()    
        for i in range(0, len(secodeInfo)):        
            security = secodeInfo[i][0] + '.'
            if secodeInfo[i][1] == 'SZ':
                security = security + 'SZSE'
            if secodeInfo[i][1] == 'SH':
                security = security + 'SSE'
            security = str(security)

            desTableName = '[HistData].[dbo].[LCY_STK_01MS_' + secodeInfo[i][1] +'_' + secodeInfo[i][0] + "]"
            securities = [];
            securities.append(security)
            fields = ["TradingDate", "TradingTime","Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
            timePeriods = [['2017-07-01 00:00:00.000', '2017-08-01 00:00:00.000']]
            timeInterval = 5
            
            ret, errMsg, dataCols = GetDataByTime(securities, [], fields, EQuoteType["k_Minute"], timeInterval, timePeriods)

            if ret == 0:
                infoStr = "[i] threadName: " + str(threading.currentThread().getName()) + "  " + security +" GetDataByTime Success! InfoCount = " + str(len(dataCols))
                recordInfoWithLock(infoStr)
                WriteToDataBaseFromNet(databaseObj, desTableName, dataCols)
            else:
                infoStr = "[x] threadName: " + str(threading.currentThread().getName()) + "  " + security + " GetDataByTime Failed: " +  errMsg  
                recordInfoWithLock(infoStr)
        databaseObj.CloseConnect()
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
        if srcName == 'Net':
            WriteNetData(secodeInfo)
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

    secodeInfo = GetSecodeInfo()
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

'''
作用：获取所有证券的历史数据
过程：1. 从数据库获取证券的代码信息。
     2. 根据CPU的数目和证券数设置读写线程的个数。
     3. 将证券代码信息按照线程数均分给不同的线程。
'''
def GetHistDataMultiThread(srcName):
    try: 
        global g_susCount
        secodeInfo = GetSecodeInfo()
        databaseTable = GetDatabaseTableInfo()
        
        if srcName == "Excel":
            addedSecodeInfo, secodeInfo = getCompleteSecodeInfoByExcel(secodeInfo, EXCELFILE_DIR)        

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

def testNetInterface():
    print "username: %s, password: %s" %(QT_USR, QT_PWD)

    # testApi = TestApi()

    # testApi.QtLogin(qt_usr, qt_pwd)

    # GetHistDataSingleThread()

    # testApi.QtLogout(qt_usr)

    # sys.exit(0)

def testExcelInterface():
    srcName = "Excel"
    GetHistDataMultiThread(srcName)

def main():
    testExcelInterface()

if __name__ == "__main__":
    main()
