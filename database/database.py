from example import MSSQL 

def createTable(databaseObj):
    tableCount = 10
    for i in range(1,tableCount):
        tableName = "[dbo].[ATestTable_" + str(i) + "]"
        valueStr = "(TDATE int, TIME int, SECODE varchar(10), \
                    TOPEN decimal(10,4), TCLOSE decimal(10,4), HIGH decimal(10,4), LOW decimal(10,4), \
                    VATRUNOVER decimal(18,4), VOTRUNOVER decimal(18,4), PCTCHG decimal(10,4))"
        createStr = "create table " + tableName + valueStr
        databaseObj.ExecStoreProduce(createStr)

def main():
    databaseObj = MSSQL()
    if databaseObj.VerifyConnection():
        createTable(databaseObj)

if __name__ == "__main__":
    main()