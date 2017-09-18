from example import MSSQL
import traceback
import threading
from toolFunc import *



def createRealTable(databaseObj):
    startIndex = 1
    endIndex = 11
    try:
        for i in range(startIndex, endIndex):
            if i < 10: 
                tableName = "[dbo].[LCY_STK_01MS_SZ_00000" + str(i) + "]"
            elif 9 < i < 100:
                tableName = "[dbo].[LCY_STK_01MS_SZ_0000" + str(i) + "]"
            elif 99 < i < 1000:
                tableName = "[dbo].[LCY_STK_01MS_SZ_000" + str(i) + "]"

            valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                        TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                        VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
            createStr = "create table " + tableName + valueStr
            databaseObj.ExecStoreProduce(createStr)
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "createRealTable  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr            

def dropRealTable(databaseObj):
    startIndex = 1
    endIndex = 11
    try: 
        for i in range(startIndex, endIndex):
            if i < 10: 
                tableName = "[dbo].[LCY_STK_01MS_SZ_00000" + str(i) + "]"
            elif 9 < i < 100:
                tableName = "[dbo].[LCY_STK_01MS_SZ_0000" + str(i) + "]"
            elif 99 < i < 1000:
                tableName = "[dbo].[LCY_STK_01MS_SZ_000" + str(i) + "]"
            dropStr = "drop table " + tableName
            databaseObj.ExecStoreProduce(dropStr)
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "dropRealTable  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr

def dropAllSecodeTable(secodeInfo):
    try: 
        databaseObj = MSSQL()
        for i in range(len(secodeInfo)):
            symbol = str(secodeInfo[i][0])
            market = str(secodeInfo[i][1])
            tableName = '[HistData].[dbo].[LCY_STK_01MS_' + market +'_' + symbol + "]"
            dropTableByName(databaseObj, tableName)
        databaseObj.CloseConnect()
        return secodeInfo

    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] comleteDatabaseByExcel()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr       

def createAllSecodeTable(secodeInfo):
    try: 
        databaseObj = MSSQL()
        for i in range(len(secodeInfo)):
            symbol = str(secodeInfo[i][0])
            market = str(secodeInfo[i][1])
            tableName = '[HistData].[dbo].[LCY_STK_01MS_' + market +'_' + symbol + "]"
            createTableByName(databaseObj, tableName)
        databaseObj.CloseConnect()
        return secodeInfo

    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] comleteDatabaseByExcel()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr               

def addTableByExcel():
    try: 
        secodeInfo = GetSecodeInfo()
        execlFileDirName = "E:\DataBase\original-data-20160910-20170910-1m"

        print 'Original Secode Numb: %d' %(len(secodeInfo))

        addedSecodeInfo, secodeInfo = getCompleteSecodeInfoByExcel(secodeInfo, execlFileDirName)

        createTableBySecodeInfo(addedSecodeInfo)

        return secodeInfo

    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] comleteDatabaseByExcel()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr            

def createCompleteExeclTable():
    try: 
        secodeInfo = GetSecodeInfo()
        execlFileDirName = "E:\DataBase\original-data-20160910-20170910-1m"

        print 'Original Secode Numb: %d' %(len(secodeInfo))

        addedSecodeInfo, secodeInfo = getCompleteSecodeInfoByExcel(secodeInfo, execlFileDirName)

        addTableBySecodeInfo(secodeInfo, GetDatabaseTableInfo())

        # createAllSecodeTable(secodeInfo)

        return secodeInfo

    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] createCompleteExeclTable()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr       

def dropCompleteExeclTable():
    try: 
        secodeInfo = GetSecodeInfo()
        execlFileDirName = "E:\DataBase\original-data-20160910-20170910-1m"

        print 'Original Secode Numb: %d' %(len(secodeInfo))

        addedSecodeInfo, secodeInfo = getCompleteSecodeInfoByExcel(secodeInfo, execlFileDirName)

        dropAllSecodeTable(secodeInfo)

        return secodeInfo

    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] createCompleteExeclTable()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr         

def testGetDatabaseTableInfo():
    databaseTable = GetDatabaseTableInfo()
    print len(databaseTable)
    print databaseTable[1:5]
    if u'LCY_STK_01MS_SH_600970' in databaseTable:
        print 'TTTTT'

def main():
    try:
        databaseObj = MSSQL()

        dropRealTable(databaseObj)
        createRealTable(databaseObj)

        databaseObj.CloseConnect()
    except:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] threadName: " + str(threading.currentThread().getName()) + "  " \
                + "main()  Failed \n" \
                + "[E] Exception : " + exceptionInfo
        print infoStr            

if __name__ == "__main__":
    # main()
    # dropAllSecodeTable()
    # comleteDatabaseByExcel()
    # dropCompleteExeclTable()
    createCompleteExeclTable()
    # testGetDatabaseTableInfo()

