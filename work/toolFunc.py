# -*- coding: UTF-8 -*-
import math
import time
from example import MSSQL
import os
import traceback
import threading
import pyodbc
from CONFIG import *

def getSimpleDate(oriDateStr):
    dateArray = oriDateStr.split(' ')
    dateStr = dateArray[0].replace('-','')
    return dateStr   

def getSimpleTime(oriTimeStr):
    timeArray = oriTimeStr.split(' ')
    timeStr = timeArray[1].replace(':','').split('.')[0]
    return timeStr   

def transExcelTimeToStr(excelTime):
    deltaDays = 70 * 365 + 19
    deltaHoursSecs = 8 * 60 * 60
    daySecs = 24 * 60 * 60
    originalDayTime = excelTime - deltaDays
    
    transSecTime = math.ceil(originalDayTime * daySecs - deltaHoursSecs)
    # print 'transSecTime: %f'%(transSecTime)
    timeArray = time.localtime(transSecTime)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # print otherStyleTime
    return otherStyleTime

def GetSecodeInfoFromDataTable():
    databaseObj = MSSQL()
    originDataTable = '[dbo].[SecodeInfo]'
    queryString = 'select SECODE, EXCHANGE from ' + originDataTable
    result = databaseObj.ExecQuery(queryString)

    databaseObj.CloseConnect()
    return result

def GetDatabaseTableInfo(databaseName):
    databaseObj = MSSQL()
    queryString = "select name from "+ databaseName +"..sysobjects where xtype= 'U'"
    result = databaseObj.ExecQuery(queryString)
    transRst = []
    for i in range(len(result)):
        transRst.append(str(result[i][0]))
    databaseObj.CloseConnect()
    return transRst    

def LogInfo(wfile, info):
    wfile.write(info)    
    print info    

def getInsertStockDataStr(result, desTableName):
    colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
    TDATE = getSimpleDate(result[0])
    TIME = getSimpleTime(result[0])
    SECODE = result[1]
    TOPEN = result[2]
    TCLOSE = result[3]
    HIGH = result[4]
    LOW = result[5]
    VOTRUNOVER = result[6]
    VATRUNOVER = result[7]
    TYClOSE = result[8]
    PCTCHG = (TCLOSE - TYClOSE) / TYClOSE

    valStr = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
            + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
            + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG)  

    insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
    return insertStr
        

def getMarketDataTslStr(secode, startDate, endDate, logFile):
    # secode = 'SH000001'
    # startDate = "20170901" 
    # endDate = "20170902"
    try:
        tslStr = "code := \'" + secode + "\'; \
        beginDate := " + str(startDate) + "; \
        endDate := " + str(endDate) + "; \
        begt:=inttodate(beginDate); \
        endt:=inttodate(endDate); \
        Setsysparam(PN_Cycle(),cy_1m()); \
        return select datetimetostr(['date']) as 'date',\
        ['StockID'] as 'secode', ['open'] as 'open',  ['close'] as 'close', \
        ['high']as 'high', ['low']as 'low', ['amount'] as 'VATRUNOVER', ['vol'] as 'VOTRUNOVER',['yclose'] as 'yclose'\
        from markettable datekey  begt to endt of code end;"
        # print tslStr
        return tslStr
    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetMarketDataTslStr Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr)    

def getStockGoMarkerTime(curs, secode, logFile):
    try:
        tslStr = "stockId:='SZ000002';SetSysParam(PN_Stock(), stockId); result:=StockGoMarketDate();return result;" 
        stockGoMarkertTime = curs.execute(tslStr)
        return stockGoMarkertTime
    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetStockGoMarkerTime Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr)          


def getDownloadedDataStartEndTime(tableName):
    startTime = 0
    endTime = 0
    return startTime, endTime

def getCurStartEndTime(secode):
    curStartTime = 0
    curEndTime = 0
    return curStartTime, curEndTime

def dropTableByName(databaseObj, tableName):
    try:
        # valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
        #             TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
        #             VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        sqlStr = "drop table " + tableName 
        databaseObj.ExecStoreProduce(sqlStr)
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] deleteTableByName  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr  

def createTableByName(databaseObj, tableName):
    try:
        valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                    TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                    VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        sqlStr = "create table " + tableName + valueStr
        databaseObj.ExecStoreProduce(sqlStr)
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] createTableByName  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr  

def deleteSecodeInfoFromExcel(secodeInfo, execlFileDirName):
    try:
        excelFileNameArray = os.listdir(execlFileDirName)
        i = 0
        deletedSecodeInfo = []
        while i < len(secodeInfo):      
            symbol = str(secodeInfo[i][0])
            market = str(secodeInfo[i][1])
            security = symbol + market
            fileName = market + symbol + '.xlsx'    
            if fileName not in excelFileNameArray:
                secodeInfo.pop(i)       
                deletedSecodeInfo.append([symbol,market])   
                continue
            i = i + 1
        return deletedSecodeInfo, secodeInfo
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] completeSecodeInfo  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr   
        return -1, secodeInfo   

def AddSecodeInfoFromExcel(secodeInfo, execlFileDirName):
    try:
        excelFileNameArray = os.listdir(execlFileDirName)
        secodeExelFileName = []
        for i in range (len(secodeInfo)):
            symbol = str(secodeInfo[i][0])
            market = str(secodeInfo[i][1])
            fileName = market + symbol + '.xlsx'            
            secodeExelFileName.append(fileName)
 
        addedSecodeInfo = []
        for i in range(len(excelFileNameArray)):            
            if excelFileNameArray[i] not in secodeExelFileName:            
                symbol = excelFileNameArray[i][2:8]
                market = excelFileNameArray[i][0:2]
                secodeInfo.append([symbol,market])
                addedSecodeInfo.append([symbol,market])
        return addedSecodeInfo, secodeInfo
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] completeSecodeInfo  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr   
        return -1, secodeInfo

def addTableBySecodeInfo(secodeInfo, databaseTable):
    try:
        databaseObj = MSSQL()
        addedNumb = 0
        for i in range(len(secodeInfo)):
            tableName = DATABASE_TABLE_PREFIX + secodeInfo[i][1] +'_' + secodeInfo[i][0]
            wholeTableName = '[HistData].[dbo].'+ '[' + tableName + ']'
            if tableName not in databaseTable:
                print 'tableName: ' + tableName
                createTableByName(databaseObj, wholeTableName)  
                addedNumb = addedNumb + 1  
        databaseObj.CloseConnect()
        return addedNumb
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] addTableBySecodeInfo()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr   
        return -1

def createTableBySecodeInfo(secodeInfo):
    try: 
        databaseObj = MSSQL()
        for i in range(len(secodeInfo)):
            symbol = str(secodeInfo[i][0])
            market = str(secodeInfo[i][1])
            tableName = '[HistData].[dbo].[LCY_STK_01MS_' + market +'_' + symbol + "]"
            createTableByName(databaseObj, tableName)
        databaseObj.CloseConnect()
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "\n[X] addTableBySecodeInfo  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr   

def getSecodeInfoFromTianRuan(logFile):
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        tslStr = u"name:='A股';StockID:=getbk(name);return StockID;"
        curs.execute(tslStr)
        result = curs.fetchall()
        curs.close()
        conn.close()
        transResult = []
        for data in result:
            transResult.append(data[0])
        return transResult
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        exceptionInfo.decode('unicode_escape')
        LogInfo(logFile, exceptionInfo)    
    
def getCompleteSecodeInfoByExcel(logFile, execlFileDirName):
    try: 
        secodeInfo = GetSecodeInfoFromDataTable()
        deletedSecodeInfo, secodeInfo = deleteSecodeInfoFromExcel(secodeInfo, execlFileDirName)
        print 'Deleted Secode Numb: %d, Afte delete Secode Numb : %d' %(len(deletedSecodeInfo), len(secodeInfo))

        addedSecodeInfo, secodeInfo = AddSecodeInfoFromExcel(secodeInfo, execlFileDirName)
        print 'Added Secode Numb: %d, Afte add Secode Numb : %d' %(len(addedSecodeInfo), len(secodeInfo))   

        return addedSecodeInfo, secodeInfo
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] getCompleteSecodeInfoByExcel()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, exceptionInfo)         
'''
功能：提取用户和密码
返回值为：(ret, usr, pwd)
'''
def GetUsrPwd(filename):
    if os.path.exists(filename):
        pass
    else:
        return (False, "", "")

    usr = None
    pwd = None
    f = open(filename, "r")

    line = f.readline()
    strs = line.split(':')
    if 0 == len(strs):
        f.close()
        return (False, "", "")
    usr = strs[1].strip()
    line = f.readline()
    strs = line.split(':')
    if 0 == len(strs):
        f.close()
        return (False, "", "")
    pwd = strs[1].strip()
    f.close()

    return (True, usr, pwd)