import os, pymssql

from multiprocessing import cpu_count
import datetime
import threading

from example import MSSQL 

g_DatabaseObj = MSSQL();

g_TestSingleThread = False;
g_TestMultiThread = True;

class TestMSSQL(object):
    def __init__(self):
        self.__name__ = "TestMSSQL"

    def testQuery(self, databaseObj):
        queryString = 'select SECODE, EXCHANGE from [dbo].[SecodeInfo]'
        result = databaseObj.ExecQuery(queryString)
        print len(result)
        # print type(result)
        # print type(result[1])
        # print result[1][0], result[1][1]

    def testInsert(self, databaseObj):    
        TDate = 15
        secode = '000004'
        insertStr = "insert into [dbo].[ATestTable](TDATE, SECODE) values ("+ str(TDate) + ", \'"+ secode +"\')"
        # insertStr = "insert into [dbo].[ATestTable](TDATE, SECODE) values (14, '000003')"
        print insertStr
        insertRst = databaseObj.ExecStoreProduce(insertStr)
        print insertRst    

    def testInsertFromTable(self, databaseObj):
        originDataTable = '[dbo].[SecodeInfo]'
        desDataTable = '[dbo].[BTestTable]'

        queryString = 'select SECODE, EXCHANGE from ' + originDataTable
        result = databaseObj.ExecQuery(queryString)
        resultRows = len(result)
        print 'result rows: ' + str(resultRows)

        starttime = datetime.datetime.now()
        print "Start Time: %s" %(starttime)

        for i in range(0, resultRows):
            secode = result[i][0]
            insertStr = "insert into "+ desDataTable + "(TDATE, SECODE) values ("+ str(i) + ", \'"+ secode +"\')"
            insertRst = databaseObj.ExecStoreProduce(insertStr)

        endtime = datetime.datetime.now()
        deletaTime = endtime - starttime
        print "End Time: %s" %(endtime)
        print 'Single Thread Running Time: %d%s' %(deletaTime.seconds, "s")


def InsertFromTable(databaseObj, desDataTable, result):    
    print 'Insert To Table: ' + desDataTable
    for i in range(0, len(result)):
        secode = result[i][0]
        insertStr = "insert into "+ desDataTable + "(TDATE, SECODE) values ("+ str(i) + ", \'"+ secode +"\')"
        insertRst = databaseObj.ExecStoreProduce(insertStr)    

def TestMultiThreadInsert():
    originDataTable = '[dbo].[SecodeInfo]'
    queryString = 'select SECODE, EXCHANGE from ' + originDataTable
    result = g_DatabaseObj.ExecQuery(queryString)    

    resultRows = len(result)
    numbInterval = len(result) / cpu_count()
    threadCount = cpu_count()
    if len(result) % cpu_count() != 0:
        threadCount = threadCount + 1

    print 'resultRows: %d, numbInterval: %d, threadCount: %d' %(len(result), numbInterval, threadCount)

    threads = [];
    desDataTables = ["[dbo].[TestTable1]", "[dbo].[BTestTable2]"];

    for i in range(0, threadCount):
        startIndex = i * numbInterval
        endIndex = min((i+1) * numbInterval, len(result))
        print (startIndex, endIndex)
        databaseObj = MSSQL();
        desDataTables = "[dbo].[ATestTable_"+ str(i) +"]"
        if databaseObj.VerifyConnection():
            threads.append(threading.Thread(target=InsertFromTable, args=(databaseObj, desDataTables, result)))    

    #     # tmp = threading.Thread(target=InsertFromTable, args=(result, startIndex, endIndex))
    #     # threads.append(tmp)   

    # for i in range(0, threadCount):
    #     databaseObj = MSSQL();
    #     if databaseObj.VerifyConnection():
    #         threads.append(threading.Thread(target=InsertFromTable, args=(databaseObj, desDataTables[i], result)))

    starttime = datetime.datetime.now()
    print "Start Time: %s" %(starttime)

    for thread in threads:
        thread.setDaemon(True)
        thread.start();
    thread.join()
    
    endtime = datetime.datetime.now()
    deletaTime = endtime - starttime
    print "End Time: %s" %(endtime)
    print 'Multi Thread Running Time: %d%s' %(deletaTime.seconds, "s")

def main():
    if g_TestSingleThread:
        databaseObj = MSSQL()        
        if databaseObj.VerifyConnection():
            testObj = TestMSSQL()
            # testObj.testQuery(databaseObj)
            # testObj.testInsert(databaseObj)
            testObj.testInsertFromTable(databaseObj)

    if g_TestMultiThread:
        TestMultiThreadInsert()

def test():
    conn=pymssql.connect(host='localhost',user='sa',password='sa',database='HistData')  

    cur=conn.cursor()  
    
    cur.execute('select SECODE from [dbo].[SecodeInfo]')  

    print (cur.fetchall())  
    
    cur.close()  
    
    conn.close()      

if __name__ == "__main__":
    main()