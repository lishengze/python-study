import pymssql
import xlrd
import datetime
from toolFunc import getSimpleDate, getSimpleTime, transExcelTimeToStr, getSecodeInfo
from example import MSSQL



def testReadData():
    databaseObj = MSSQL()
    secodeInfo = getSecodeInfo(databaseObj)
    print 'SecodeInfo Len: %d' % (len(secodeInfo))

    startTime = datetime.datetime.now()
    print '\n++++++++ Start Time: %s ++++++++\n' %(str(startTime)) 

    symbol = str(secodeInfo[0][0])
    market = str(secodeInfo[0][1])
    fileName = market + symbol + '.xlsx'
    dirName =  "E:\DataBase\original-data-20160910-20170910-1m"
    completeFileName = dirName + "\\" + fileName
    desTableName = '[HistData].[dbo].[LCY_STK_01MS_' + secodeInfo[0][1] +'_' + secodeInfo[0][0] + "]"

    print 'desTableName: %s'%(desTableName)
    print 'completeFileName: %s'%(completeFileName)

    bk = xlrd.open_workbook(completeFileName)
    try:
		result = bk.sheet_by_name("Sheet1")      
    except:
		print "Read From Xlsx Error!"

    nrows = result.nrows
    ncols = result.ncols
    print "Result Numb:  %d" % (nrows)

    for i in range(1, 2):
        colStr = " (TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        dateTimeStr = transExcelTimeToStr(result.cell_value(i, 2))
        TDATE = getSimpleDate(dateTimeStr)
        TIME = getSimpleTime(dateTimeStr)
        SECODE = str(result.cell_value(i, 0))[2:]
        TOPEN = result.cell_value(i, 4)
        TCLOSE = result.cell_value(i, 5)
        HIGH = result.cell_value(i, 6)
        LOW = result.cell_value(i, 7)
        VOTRUNOVER = result.cell_value(i, 8)
        VATRUNOVER = result.cell_value(i, 9)
        PCTCHG = (TOPEN - result.cell_value(i, 11)) / result.cell_value(i, 11)

        valStr = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG)  

        insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
        # print insertStr
        databaseObj.ExecStoreProduce(insertStr)
        
    endTime = datetime.datetime.now()
    costTime = endTime - startTime

    print 'End Time: %s'%(str(endTime))
    print '++++++++ Read one file from excel cost time: %s ++++++++' % (str(costTime.seconds))       

if __name__ == "__main__":
    testReadData()