from example import MSSQL

def createDataByTimeTable(databaseObj):
    startIndex = 0
    endIndex = 20
    for i in range(startIndex, endIndex):
        tableName = "[dbo].[LCY_STK_01MS_" + str(i) + "]"
        valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                    TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                    VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        createStr = "create table " + tableName + valueStr
        databaseObj.ExecStoreProduce(createStr)

def createRealTable(databaseObj):
    startIndex = 1
    endIndex = 11
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

def dropRealTable(databaseObj):
    startIndex = 1
    endIndex = 11
    for i in range(startIndex, endIndex):
        if i < 10: 
            tableName = "[dbo].[LCY_STK_01MS_SZ_00000" + str(i) + "]"
        elif 9 < i < 100:
            tableName = "[dbo].[LCY_STK_01MS_SZ_0000" + str(i) + "]"
        elif 99 < i < 1000:
            tableName = "[dbo].[LCY_STK_01MS_SZ_000" + str(i) + "]"
        dropStr = "drop table " + tableName
        databaseObj.ExecStoreProduce(dropStr)


def dropTable(databaseObj):
    startIndex = 0
    endIndex = 10
    for i in range(startIndex, endIndex):
        tableName = "[dbo].[ATestTable_" + str(i) + "]"
        dropStr = "drop table " + tableName
        databaseObj.ExecStoreProduce(dropStr)

def createExchangeData(databaseObj):
    tableName = "[dbo].[AExchangeData]"
    valueStr = "(CoutryCode varchar(10), ENName varchar(50), Market varchar(10), Marketname varchar(50))"
    createStr = "create table " + tableName + valueStr    
    databaseObj.ExecStoreProduce(createStr)

def insertDatetime(databaseObj):
    desTableName = "[dbo].[ATestTime]"
    colStr = "(time)"
    valStr = "2017-07-03 09:30:00.000"
    # insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
    insertStr = "insert into [dbo].[ATestTable_2] (TDATE, TIME) values (20170703, 093000)"
    databaseObj.ExecStoreProduce(insertStr)    

def GetSecodeInfo(databaseObj):
    originDataTable = '[dbo].[SecodeInfo]'
    queryString = 'select SECODE, EXCHANGE from ' + originDataTable
    result = databaseObj.ExecQuery(queryString)
    return result


def main():
    databaseObj = MSSQL()
    if databaseObj.VerifyConnection():        
        # dropTable(databaseObj)
        # createDataByTimeTable(databaseObj)
        # createExchangeData(databaseObj)
        # GetSecodeInfo(databaseObj)
        # insertDatetime(databaseObj)
        dropRealTable(databaseObj)
        createRealTable(databaseObj)

def test():
    databaseObj = MSSQL()
    dropRealTable(databaseObj)
    createRealTable(databaseObj)
    databaseObj.CloseConnect()

if __name__ == "__main__":
    # main()
    test()
