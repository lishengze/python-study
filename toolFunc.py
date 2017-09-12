# -*- coding: UTF-8 -*-
def getSimpleDate(oriDateStr):
    dateArray = oriDateStr.split(' ')
    dateStr = dateArray[0].replace('-','')
    return dateStr   

def getSimpleTime(oriTimeStr):
    timeArray = oriTimeStr.split(' ')
    timeStr = timeArray[1].replace(':','').split('.')[0]
    return timeStr   

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