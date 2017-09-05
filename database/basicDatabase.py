from example import MSSQL

def createTable(databaseObj):
    startIndex = 0
    endIndex = 20
    for i in range(startIndex, endIndex):
        tableName = "[dbo].[ATestTable_" + str(i) + "]"
        valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                    TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                    VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        createStr = "create table " + tableName + valueStr
        databaseObj.ExecStoreProduce(createStr)

def dropTable(databaseObj):
    startIndex = 0
    endIndex = 20
    for i in range(startIndex, endIndex):
        tableName = "[dbo].[ATestTable_" + str(i) + "]"
        dropStr = "drop table " + tableName
        databaseObj.ExecStoreProduce(dropStr)

def main():
    databaseObj = MSSQL()
    if databaseObj.VerifyConnection():
        # dropTable(databaseObj)
        createTable(databaseObj)

if __name__ == "__main__":
    main()