# -*- coding: UTF-8 -*-
from toolFunc import *
from example import MSSQL
import pyodbc
import traceback
import datetime
import threading
import math

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
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr) 

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
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr)    

def completeDatabaseTable (databaseName, tableNameArray, logFile):
    try:
        databaseObj = MSSQL() 
        tableInfo = GetDatabaseTableInfo(databaseName)
        # print tableInfo
        for tableName in tableNameArray:
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'
            if tableName not in tableInfo:
                createTableByName(databaseObj, completeTableName)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr) 

def refreshTestDatabase(databaseName, tableNameArray, logFile):
    try:
        databaseObj = MSSQL() 
        tableInfo = GetDatabaseTableInfo(databaseName)
        # print tableInfo
        for tableName in tableNameArray:
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

            if tableName in tableInfo:
                dropTableByName(databaseObj, completeTableName)
                # print completeTableName
            createTableByName(databaseObj, completeTableName)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr)         

def refreshHistDatrabase(databaseName, tableNumb, logFile):
    try:
        databaseObj = MSSQL() 
        tableInfo = GetDatabaseTableInfo(databaseName)
        # print tableInfo
        for i in range(tableNumb):
            tableName = str(i)
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

            if tableName in tableInfo:
                dropTableByName(databaseObj, completeTableName)
                # print completeTableName
            createTableByName(databaseObj, completeTableName)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr) 

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
        return result        
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "GetMarketDataTslStr Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr)        

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
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr)     

def getStartEndTime(oriStartTime, oriEndTime, database, table, logFile):
    try:
        timeArray = []
        tableDataStartTime, tableDataEndTime = getTableDataStartEndTime(database, table, logFile)
        if tableDataStartTime is None or tableDataEndTime is None:
            timeArray.append([oriStartTime, oriEndTime])
        else:
            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                startTime = addOneDay(tableDataEndTime)
                endTime = oriEndTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                endTime = minusOneDay(tableDataStartTime)
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                timeArray.append([oriStartTime, minusOneDay(tableDataStartTime)])
                timeArray.append([addOneDay(tableDataEndTime), oriEndTime])

        return timeArray
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception : " + exceptionInfo
        LogInfo(logFile, infoStr) 
        raise(Exception(infoStr))