# -*- coding: UTF-8 -*-
import math
import time

def getSimpleDate(oriDateStr):
    dateArray = oriDateStr.split(' ')
    dateStr = dateArray[0].replace('-','')
    return dateStr   

def getSimpleTime(oriTimeStr):
    timeArray = oriTimeStr.split(' ')
    timeStr = timeArray[1].replace(':','').split('.')[0]
    return timeStr   

def transExcelTimeToStr(excelTime):
    deltaDays = 70 * 365 + 19
    deltaHoursSecs = 8 * 60 * 60
    daySecs = 24 * 60 * 60
    originalDayTime = excelTime - deltaDays
    
    transSecTime = math.ceil(originalDayTime * daySecs - deltaHoursSecs)
    # print 'transSecTime: %f'%(transSecTime)
    timeArray = time.localtime(transSecTime)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # print otherStyleTime
    return otherStyleTime

def getSecodeInfo(databaseObj):
    originDataTable = '[dbo].[SecodeInfo]'
    queryString = 'select SECODE, EXCHANGE from ' + originDataTable
    result = databaseObj.ExecQuery(queryString)
    return result

'''
功能：提取用户和密码
返回值为：(ret, usr, pwd)
'''
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