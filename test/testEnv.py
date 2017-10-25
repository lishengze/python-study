# -*- coding: UTF-8 -*-
import pyodbc
import traceback
# import sys
# reload(sys)
# sys.setdefaultencoding("gbk")

g_logFileName = "log.txt"
g_logFile = open(g_logFileName, 'w')

def recordInfo(str):
    print str
    g_logFile.write(str + '\n')

def getMarketDataTslStr():
    # tslStr = "setsysparam(pn_stock(),'SZ000002');setsysparam(pn_date(), today()); return nday(30, 'date', datetimetostr(sp_time()), 'open', open(), 'close', close());"
    # tslStr = u"setsysparam(pn_stock(), 'SZ000002'); return datetostr(firstday());"
    # tslStr = "stockId:='SZ000002';SetSysParam(PN_Stock(), stockId); return datetostr(StockGoMarketDate ());"
    # tslStr = u"name:='A股';StockID:=getbk(name);return StockID;"
    # tslStr = "stockId:='SZ000002';SetSysParam(PN_Stock(), stockId); result:=StockGoMarketDate();return result;"
    code = 'SH000001'
    startDate = "20170901" 
    endDate = "20170902"
    tslStr = "code := \'" + code + "\'; \
     beginDate := " + startDate + "; \
     endDate := " + endDate + "; \
     begt:=inttodate(beginDate); \
     endt:=inttodate(endDate); \
     Setsysparam(PN_Cycle(),cy_1m()); \
     return select datetimetostr(['date']) as 'date',\
     ['StockID'] as 'secode', ['open'] as 'open',  ['close'] as 'close', \
     ['high']as 'high', ['low']as 'low', ['vol'] as 'VOTRUNOVER', ['amount'] as 'VATRUNOVER'\
     from markettable datekey  begt to endt of code end;"
    print tslStr
    return tslStr

def getMarketFirstDayTslStr():
    tslStr = "setsysparam(pn_stock(),'SZ000002');setsysparam(pn_date(), today()); return nday(30, 'date', datetimetostr(sp_time()), 'open', open(), 'close', close());"
    # tslStr = u"setsysparam(pn_stock(), 'SZ000002'); return datetostr(firstday());"
    # tslStr = "stockId:='SZ000002';SetSysParam(PN_Stock(), stockId); return datetostr(StockGoMarketDate ());"
    # tslStr = u"name:='A股';StockID:=getbk(name);return StockID;"
    # tslStr = "stockId:='SZ000002';SetSysParam(PN_Stock(), stockId); result:=StockGoMarketDate();return result;"    
    return tslStr

def basicTest():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        tslStr = getMarketFirstDayTslStr();
        curs.execute(tslStr)
        result = curs.fetchall()
        curs.close()
        conn.close()
        print(result)
    except Exception as e:       
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        exceptionInfo.decode('unicode_escape')
        recordInfo(exceptionInfo)

if __name__ == "__main__":
    basicTest()