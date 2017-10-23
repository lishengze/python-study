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

def basicTest():
    try:
        dataSource = "dsn=t1"
        conn = pyodbc.connect(dataSource)
        curs = conn.cursor()
        tslStr = "setsysparam(pn_stock(),'SZ000002');setsysparam(pn_date(), today()); return nday(30, 'date', datetimetostr(sp_time()), 'open', open(), 'close', close());"
        curs.execute(tslStr)
        rows = curs.fetchall()
        curs.close()
        conn.close()
        print(rows)
    except Exception as e:       
        # print "exception" 
        # traceback.print_exc(file = g_logFile)
        # traceback.print_exc()
        exceptionInfo = "\n" + str(traceback.format_exc()) + '\n'
        exceptionInfo.decode('unicode_escape')
        # exceptionInfo.decode('gbk').encode('utf-8')
        recordInfo(exceptionInfo)

if __name__ == "__main__":
    basicTest()