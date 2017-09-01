import os, pymssql
from example import MSSQL 


def testQuery(databaseObj):
    queryString = 'select SECODE, EXCHANGE from [dbo].[SecodeInfo]'
    result = databaseObj.ExecQuery(queryString)
    print len(result)
    # print type(result)
    # print type(result[1])
    # print result[1][0], result[1][1]

def testInsert(databaseObj):    
    TDate = 15
    secode = '000004'
    insertStr = "insert into [dbo].[ATestTable](TDATE, SECODE) values ("+ str(TDate) + ", \'"+ secode +"\')"
    # insertStr = "insert into [dbo].[ATestTable](TDATE, SECODE) values (14, '000003')"
    print insertStr
    insertRst = databaseObj.ExecStoreProduce(insertStr)
    print insertRst    

def testInsertFromTable(databaseObj):
    queryString = 'select SECODE, EXCHANGE from [dbo].[SecodeInfo]'
    result = databaseObj.ExecQuery(queryString)
    resultRows = len(result)
    print 'result rows: ' + str(resultRows)
    
    for i in range(0, resultRows):
        secode = result[i][0]
        insertStr = "insert into [dbo].[ATestTable](TDATE, SECODE) values ("+ str(i) + ", \'"+ secode +"\')"
        insertRst = databaseObj.ExecStoreProduce(insertStr)

def main():
    databaseObj = MSSQL()    
    if databaseObj.VerifyConnection():
        # testQuery(databaseObj)
        # testInsert(databaseObj)
        testInsertFromTable(databaseObj)

def test():
    conn=pymssql.connect(host='localhost',user='sa',password='sa',database='HistData')  

    cur=conn.cursor()  
    
    cur.execute('select SECODE from [dbo].[SecodeInfo]')  

    print (cur.fetchall())  
    
    cur.close()  
    
    conn.close()      

if __name__ == "__main__":
    main()