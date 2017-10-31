# -*- coding: UTF-8 -*-
import math
import time
from example import MSSQL
import os
import traceback
import threading
import pyodbc
from CONFIG import *

def LogInfo(wfile, info):
    try:
        wfile.write(info)    
        print info    
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] LogInfo Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        raise(Exception(infoStr)) 

# def getCompleteSecodeInfoByExcel(logFile, execlFileDirName):
#     try: 
#         secodeInfo = GetSecodeInfoFromDataTable(logFile)
#         deletedSecodeInfo, secodeInfo = deleteSecodeInfoFromExcel(secodeInfo, execlFileDirName, logFile)
#         print 'Deleted Secode Numb: %d, Afte delete Secode Numb : %d' %(len(deletedSecodeInfo), len(secodeInfo))

#         addedSecodeInfo, secodeInfo = AddSecodeInfoFromExcel(secodeInfo, execlFileDirName, logFile)
#         print 'Added Secode Numb: %d, Afte add Secode Numb : %d' %(len(addedSecodeInfo), len(secodeInfo))   

#         return addedSecodeInfo, secodeInfo
#     except:
#         exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
#         infoStr = "[X] getCompleteSecodeInfoByExcel()  Failed \n" \
#                 + "[E] Exception :  \n" + exceptionInfo
#         LogInfo(logFile, infoStr)    
#         raise(Exception(infoStr))     

def getUsrPwd(filename, logFile):
    try:
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
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] getCompleteSecodeInfoByExcel()  Failed \n" \
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
        
def createTableBySecodeInfo(secodeInfo, logFile):
    try: 
        databaseObj = MSSQL()
        for i in range(len(secodeInfo)):
            symbol = str(secodeInfo[i][0])
            market = str(secodeInfo[i][1])
            tableName = '[HistData].[dbo].[LCY_STK_01MS_' + market +'_' + symbol + "]"
            createTableByName(databaseObj, tableName, logFile)
        databaseObj.CloseConnect()
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "\n[X] addTableBySecodeInfo  Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)  
        raise(Exception(infoStr))

    def deleteSecodeInfoFromExcel(secodeInfo, execlFileDirName, logFile):
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
                    + "[E] Exception :  \n" + exceptionInfo
            LogInfo(logFile, infoStr)  
            raise(Exception(infoStr))  

def AddSecodeInfoFromExcel(secodeInfo, execlFileDirName, logFile):
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
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)    
        raise(Exception(infoStr))

def GetSecodeInfoFromDataTable(logFile):
    try:
        databaseObj = MSSQL()
        originDataTable = '[dbo].[SecodeInfo]'
        queryString = 'select SECODE, EXCHANGE from ' + originDataTable
        result = databaseObj.ExecQuery(queryString)

        databaseObj.CloseConnect()
        return result
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] GetSecodeInfoFromDataTable Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)    
        raise(Exception(infoStr)) 

def transExcelTimeToStr(excelTime):
    try:
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
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] TransExcelTimeToStr  Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)    
        raise(Exception(infoStr)) 

def addTableBySecodeInfo(secodeInfo, databaseTable, logFile):
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
                + "[E] Exception :  \n" + exceptionInfo
        LogInfo(logFile, infoStr)  
        raise(Exception(infoStr))        