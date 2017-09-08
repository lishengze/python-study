# -*- coding: UTF-8 -*-
import time
import pickle
from QtAPI import *
from QtDataAPI import *
from example import MSSQL
from TestApi import TestApi

from multiprocessing import cpu_count
import datetime
import threading

g_toScreen = False  # 提取的数据是否输出到屏幕
g_toFile   = True   # 提取的数据是否输出到文件
g_toGBK    = False  # 提取的数据是否进行汉字编码转换

g_DatabaseObj = MSSQL();

# 提取用户和密码
# 返回值为：(ret, usr, pwd)
def GetUsrPwd(filename):
    if os.path.exists(filename):
        pass
    else:
        return (False, "", "")

    usr = None
    pwd = None
    f = open(filename, "r")

    line = f.readline()
    strs = line.split(':')
    if 0 == len(strs):
        f.close()
        return (False, "", "")
    usr = strs[1].strip()
    line = f.readline()
    strs = line.split(':')
    if 0 == len(strs):
        f.close()
        return (False, "", "")
    pwd = strs[1].strip()
    f.close()

    return (True, usr, pwd)


# UTF-8转换为GBK编码
def ConvertStr(data):
    if ~g_toGBK:
        return data
    nLen = len(data)
    if nLen == 0:
        return data
    for col_name in data.columns:
        if type(data.ix[0, col_name]) == type('str'):
            for index, row in data.iterrows():
                data.ix[index,col_name] = data.ix[index,col_name].decode('UTF-8').encode('GBK')
    return data


'''
功能：将数据写入数据库
'''
def WriteToDataBase(databaseObj, desTableName, result):
    resultRows = len(result)
    # print 'result rows: ' + str(resultRows)

    # starttime = datetime.datetime.now()
    # print "Start Time: %s" %(starttime)

    for i in range(0, resultRows):
        secode = result[i][0]
        colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        valStr = str(result.iloc[i, 0]) + ", " + str(result.iloc[i, 1]) + ", \'"+ result.iloc[i, 2] + "\'" \
                + str(result.iloc[i, 3]) + ", " + str(result.iloc[i, 4]) + ", " + str(result.iloc[i, 5]) + ", " \
                + str(result.iloc[i, 6]) + ", " + str(result.iloc[i, 7]) + ", " + str(result.iloc[i, 8]) + ", " \
                + str(result.iloc[i, 9]) + ", " + str(result.iloc[i, 10])

        insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
        # print 'insertStr: %s'%(insertStr)
        insertRst = databaseObj.ExecStoreProduce(insertStr)

    # endtime = datetime.datetime.now()
    # deletaTime = endtime - starttime
    # print "End Time: %s" %(endtime)
    # print 'Single Thread Running Time: %d%s' %(deletaTime.seconds, "s")

def GetSecodeInfo():
    originDataTable = '[dbo].[SecodeInfo]'
    queryString = 'select SECODE, EXCHANGE from ' + originDataTable
    result = g_DatabaseObj.ExecQuery(queryString)
    return result

'''
作用： 从数据源读取每个证券的历史数据并写入数据库
过程：1. 为每个线程申请一个读取数据库的类对象
     2. 循环遍历证券代码表，组合得到每只证券的代码和交易所代码，向数据源申请历史数据 
        --- 向数据源申请数据可能是线程独立的，需要用锁控制，防止并发访问造成错误
     3. 将获得数据写入数据库表中。
'''
def InsertData(secodeInfo):
    databaseObj = MSSQL()    
    for i in range(0, len(secodeInfo)):
        security = secodeInfo[i][0] + '.' + secodeInfo[i][1]
        securities = [];
        securities.append(security)
        fields = ["TradingTime","TradingDate", "Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
        timePeriods = [['2017-07-01 00:00:00.000', '2017-08-01 00:00:00.000']]
        timeInterval = 5

        # 这个操作可能无法在多个线程同时进行
        ret, errMsg, dataCols = GetDataByTime(securities, [], fields, EQuoteType["k_Minute"], timeInterval, timePeriods)

        if ret == 0:
            print "[i] GetDataByTime Success! Rows = ", len(dataCols)
            desTableName = '[dbo].LCY_STK_01MS_' + secodeInfo[i][1] +'_' + secodeInfo[i][0]
            WriteToDataBase(databaseObj, desTableName, dataCols)

        else:
            print "[x] GetDataByTime(", hex(ret), "): ", errMsg  
'''
功能： 单线程获取所有历史数据并插入到数据库中
'''
def GetHistDataSingleThread():
    secodeInfo = GetSecodeInfo()
    databaseObj = MSSQL()

    for i in range(0, len(secodeInfo)):
        security = secodeInfo[i][0] + '.' + secodeInfo[i][1]
        securities = [];
        securities.append(security)
        fields = ["TradingTime","TradingDate", "Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
        timePeriods = [['2017-07-01 00:00:00.000', '2017-08-01 00:00:00.000']]
        timeInterval = 5
        ret, errMsg, dataCols = GetDataByTime(securities, [], fields, \
                                            EQuoteType["k_Minute"], timeInterval, timePeriods)

        if ret == 0:
            print "[i] GetDataByTime Success! Rows = ", len(dataCols)
            desTableName = '[dbo].LCY_STK_01MS_' + secodeInfo[i][1] +'_' + secodeInfo[i][0]
            WriteToDataBase(databaseObj, desTableName, dataCols)

        else:
            print "[x] GetDataByTime(", hex(ret), "): ", errMsg    

'''
作用：获取所有证券的历史数据
过程：1. 从数据库获取证券的代码信息。
     2. 根据CPU的数目和证券数设置读写线程的个数。
     3. 将证券代码信息按照线程数均分给不同的线程。
'''
def GetHistDataMultiThread():
    secodeInfo = GetSecodeInfo()
    numbInterval = len(secodeInfo) / cpu_count()
    threadCount = cpu_count()
    if len(secodeInfo) % cpu_count() != 0:
        threadCount = threadCount + 1

    print 'resultRows: %d, numbInterval: %d, threadCount: %d' %(len(secodeInfo), numbInterval, threadCount)

    threads = []
    for i in range(0, threadCount):
        startIndex = i * numbInterval
        endIndex = min((i+1) * numbInterval, len(secodeInfo))
        print (startIndex, endIndex)
        tmp = threading.Thread(target=InsertData, args=(secodeInfo[startIndex:endIndex]))
        threads.append(tmp)

    starttime = datetime.datetime.now()
    print "Start Time: %s" %(starttime)

    for thread in threads:
        thread.setDaemon()
        thread.start()
    thread.join()

    endtime = datetime.datetime.now()
    deletaTime = endtime - starttime
    print "End Time: %s" %(endtime)
    print 'Multi Thread Running Time: %d%s' %(deletaTime.seconds, "s")    

'''
功能： 测试从数据源获取数据，并插入数据库中的代码是否有效。
'''
def TestGetAllHistData():
    secodeInfo = GetSecodeInfo()
    security = secodeInfo[0][0] + '.' + secodeInfo[0][1]
    print 'security: %s'%(security)
    securities = [];
    securities.append(security)
    
    fields = ["TradingTime","TradingDate", "Symbol", "OP", "CP", "HIP", "LOP", "CM", "CQ", "Change"]
    timePeriods = [['2017-07-01 00:00:00.000', '2017-08-01 00:00:00.000']]
    timeInterval = 5
    ret, errMsg, dataCols = GetDataByTime(securities, [], fields, EQuoteType["k_Minute"], timeInterval, timePeriods)

    if ret == 0:
        print "[i] GetDataByTime Success! Rows = ", len(dataCols)
        desTableName = '[dbo].ATest_' + secodeInfo[0][1] +'_' + secodeInfo[0][0]
        print 'desTableName: %s'%(desTableName)
        WriteToDataBase(desTableName, dataCols)

    else:
        print "[x] GetDataByTime(", hex(ret), "): ", errMsg    

def main():
    bret, qt_usr, qt_pwd = GetUsrPwd(os.getcwd() + "\\QtAPIDemo.id")

    print "username: %s, password: %s" %(qt_usr, qt_pwd)

    testApi = TestApi()

    testApi.QtLogin(qt_usr, qt_pwd)

    # TestGetAllHistData()

    testApi.QtLogout(qt_usr)

    sys.exit(0)

if __name__ == "__main__":
    main()
