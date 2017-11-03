# -*- coding: UTF-8 -*-
import traceback
import datetime
import math

from databaseClass import MSSQL
from toolFunc import *
from CONFIG import *

def dropTableByName(databaseObj, tableName, logFile):
    try:
        # valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
        #             TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
        #             VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        sqlStr = "drop table " + tableName 
        databaseObj.ExecStoreProduce(sqlStr)
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] deleteTableByName  Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)  
        raise(Exception(infoStr))  

def createTableByName(databaseObj, tableName, logFile):
    try:
        valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                    TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                    VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        sqlStr = "create table " + tableName + valueStr
        databaseObj.ExecStoreProduce(sqlStr)
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] createTableByName  Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)  
        raise(Exception(infoStr))  

def completeDatabaseTable (databaseName, tableNameArray, logFile):
    try:
        databaseObj = MSSQL() 
        tableInfo = getDatabaseTableInfo(databaseName, logFile)
        for tableName in tableNameArray:
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'
            if tableName not in tableInfo:
                createTableByName(databaseObj, completeTableName, logFile)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr) 
        raise(Exception(infoStr))

def refreshDatabase(databaseName, tableNameArray, logFile):
    try:
        databaseObj = MSSQL() 
        tableInfo = getDatabaseTableInfo(databaseName, logFile)
        for tableName in tableNameArray:
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

            if tableName in tableInfo:
                dropTableByName(databaseObj, completeTableName, logFile)
                # print completeTableName
            createTableByName(databaseObj, completeTableName, logFile)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)   
        raise(infoStr)      

def refreshHistDatrabase(databaseName, tableNumb, logFile):
    try:
        databaseObj = MSSQL() 
        tableInfo = getDatabaseTableInfo(databaseName, logFile)
        # print tableInfo
        for i in range(tableNumb):
            tableName = str(i)
            completeTableName = u'[' + databaseName + '].[dbo].['+ tableName +']'

            if tableName in tableInfo:
                dropTableByName(databaseObj, completeTableName, logFile)
                # print completeTableName
            createTableByName(databaseObj, completeTableName,logFile)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "refreshTestDatabase Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr) 
        raise(infoStr)

def getDatabaseTableInfo(databaseName, logFile):
    try:
        databaseObj = MSSQL()
        queryString = "select name from "+ databaseName +"..sysobjects where xtype= 'U'"
        result = databaseObj.ExecQuery(queryString)
        transRst = []
        for i in range(len(result)):
            transRst.append(str(result[i][0]))
        databaseObj.CloseConnect()
        return transRst    
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] GetDatabaseTableInfo Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)    
        raise(Exception(infoStr)) 

def getTableDataStartEndTime(databaseObj, databaseName, table):
    try:
        completeTableName = u'[' + databaseName + '].[dbo].['+ table +']'
        sqlStr = "SELECT MIN(TDATE), MAX(TDATE) FROM"  + completeTableName
        result = databaseObj.ExecQuery(sqlStr)
        startTime = result[0][0]
        endTime = result[0][1]
        return (startTime, endTime)
    except Exception as e:
        raise(e)

def addPrimaryKey(database, logFile):
    try:
        databaseObj = MSSQL() 
        databaseTableInfo = getDatabaseTableInfo(database,logFile)
        for table in databaseTableInfo:
            completeTableName = u'[' + database + '].[dbo].['+ table +']'
            alterNullColumnSqlStr = "alter table "+ completeTableName +" alter column TDATE int not null\
                                alter table "+ completeTableName +" alter column TIME int not null"
            
            databaseObj.ExecStoreProduce(alterNullColumnSqlStr)
            addPrimaryKeySqlStr = " alter table "+ completeTableName +" add primary key (TDATE, TIME)"
            databaseObj.ExecStoreProduce(addPrimaryKeySqlStr)
        databaseObj.CloseConnect()
    except Exception as e:
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        infoStr = "AddPrimaryKey Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo  
        raise(Exception(infoStr))
