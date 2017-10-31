# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from databaseClass import MSSQL
from CONFIG import *
from toolFunc import *

def getAllStockDataCostDays(oneyearAveTimeSeconds, logFile):
    stockNumb = len(getSecodeInfoFromTianRuan(logFile))
    print ("stockNumb: %d") % (stockNumb)
    year = 4
    costDays = float(oneyearAveTimeSeconds * year * stockNumb) / 3600.00 / 24.00
    print ("costDays: %f") % (costDays)
    return costDays

def simpleConnect(logFile):
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        curs.close()
        conn.close()

        infoStr = "[i] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleConnect Succeed \n"
        LogInfo(logFile, infoStr)  
        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleConnect Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(logFile, infoStr) 
        raise(infoStr)

def simpleExc(curs, logFile):
    try:
        tslStr = u"name:='A股';StockID:=getbk(name);return StockID;"
        curs.execute(tslStr)
        result = curs.fetchall()
        print len(result)
        infoStr = "[i] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleExc Succeed \n"
        LogInfo(logFile, infoStr)          
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "[X] ThreadName: " + str(threading.currentThread().getName()) + "  " \
                + "SimpleExc Failed \n" \
                + "[E] Exception : \n" + exceptionInfo
        LogInfo(logFile, infoStr)    
        raise(infoStr)

def getInsertStockDataStr(result, desTableName, logFile):
    try:
        colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        TDATE = getSimpleDate(result[0], logFile)
        TIME = getSimpleTime(result[0], logFile)
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
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetInsertStockDataStr Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)   
        raise(Exception(infoStr))   
    
def getMarketDataTslStr(secode, startDate, endDate, logFile):
    try:
        tslStr = "code := \'" + secode + "\'; \
        beginDate := " + str(startDate) + "; \
        endDate := " + str(endDate) + "; \
        begt:=inttodate(beginDate); \
        endt:=inttodate(endDate); \
        Setsysparam(PN_Cycle(),cy_1m()); \
        result := select datetimetostr(['date']) as 'date',\
        ['StockID'] as 'secode', ['open'] as 'open',  ['close'] as 'close', \
        ['high']as 'high', ['low']as 'low', ['amount'] as 'VATRUNOVER', ['vol'] as 'VOTRUNOVER',['yclose'] as 'yclose'\
        from markettable datekey  begt to endt + 0.999 of code end;\
        emptyResult := array(); \
        emptyResult[0]:= -1; \
        if result then \
            return result \
        else    \
            return emptyResult "
        # print tslStr
        return tslStr
    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetMarketDataTslStr Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)   
        raise(Exception(infoStr))   

def getStockData(code, startDate, endDate, logFile):
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        tslStr = getMarketDataTslStr(code, startDate, endDate, logFile);
        curs.execute(tslStr)
        result = curs.fetchall()
        curs.close()
        conn.close()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetStockData Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)        
        raise(Exception(infoStr))

def getTableDataStartEndTime(database, table, logFile):
    try:
        databaseObj = MSSQL() 
        completeTableName = u'[' + database + '].[dbo].['+ table +']'
        sqlStr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + completeTableName
        result = databaseObj.ExecQuery(sqlStr)
        startTime = result[0][0]
        endTime = result[0][1]
        databaseObj.CloseConnect()
        return (startTime, endTime)
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)     
        raise(infoStr)

def getStartEndTime(oriStartTime, oriEndTime, database, table, logFile):
    try:
        timeArray = []
        tableDataStartTime, tableDataEndTime = getTableDataStartEndTime(database, table, logFile)

        if tableDataStartTime is None or tableDataEndTime is None:
            timeArray.append([oriStartTime, oriEndTime])
        else:
            if oriEndTime > getIntegerDateNow(logFile):
                oriEndTime = getIntegerDateNow(logFile)

            if tableDataEndTime > getIntegerDateNow(logFile):
                tableDataEndTime = getIntegerDateNow(logFile)

            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                startTime = addOneDay(tableDataEndTime, logFile)
                endTime = oriEndTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                endTime = minusOneDay(tableDataStartTime, logFile)
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                timeArray.append([oriStartTime, minusOneDay(tableDataStartTime, logFile)])
                timeArray.append([addOneDay(tableDataEndTime, logFile), oriEndTime])

        return timeArray
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetStartEndTime Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr) 
        raise(Exception(infoStr))

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
        raise(Exception(infoStr))        

def getStockGoMarkerTime(curs, secode, logFile):
    try:
        tslStr = "stockId:='SZ000002';SetSysParam(PN_Stock(), stockId); result:=StockGoMarketDate();return result;" 
        stockGoMarkertTime = curs.execute(tslStr)
        return stockGoMarkertTime
    except:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetStockGoMarkerTime Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)          