import pymssql
import xlrd
from toolFunc import getSimpleDate, getSimpleTime, transExcelTimeToStr, getSecodeInfo
from example import MSSQL



def testReadData():
    databaseObj = MSSQL()
    secodeInfo = getSecodeInfo(databaseObj)
    print 'secodeInfo len: %d' % (len(secodeInfo))

    symbol = str(secodeInfo[0][0])
    market = str(secodeInfo[0][1])
    fileName = market + symbol + '.xlsx'
    dirName =  "E:\DataBase\original-data-20160910-20170910-1m"
    completeFileName = dirName + "\\" + fileName
    desTableName = "[dbo]"
    print 'completeFileName: %s'%(completeFileName)

    bk = xlrd.open_workbook(completeFileName)
    try:
		sh = bk.sheet_by_name("Sheet1")
    except:
		print "Error"
    nrows = sh.nrows
    ncols = sh.ncols
    print "nrows %d, ncols %d" % (nrows,ncols)

    for i in range(1, 2):
        colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        dateTimeStr = transExcelTimeToStr(sh.cell_value(i, 2))
        TDATE = getSimpleDate(dateTimeStr)
        TIME = getSimpleTime(dateTimeStr)
        SECODE = str(secodeInfo[0][0])
        TOPEN = sh.cell_value(i, 4)
        TCLOSE = sh.cell_value(i, 5)
        HIGH = sh.cell_value(i, 6)
        LOW = sh.cell_value(i, 7)
        VOTRUNOVER = sh.cell_value(i, 8)
        VATRUNOVER = sh.cell_value(i, 9)
        PCTCHG = (TOPEN - sh.cell_value(i, 11)) / sh.cell_value(i, 11)

        valStr = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG)  

        insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
        print insertStr
 
    # for i in range(0, 15):
    #     print sh.cell_value(1, i)


if __name__ == "__main__":
    testReadData()