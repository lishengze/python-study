# -*- coding: UTF-8 -*-
import math

import os
import traceback
import threading
import pyodbc
import datetime
import math

from CONFIG import *

def LogInfo(wfile, info):
    try:
        wfile.write(info)    
        print info    
    except Exception as e:
        exceptionInfo = '\n' + str(traceback.format_exc()) + '\n'
        infoStr = "[X] LogInfo Failed \n" \
                + "[E] Exception :  \n" + exceptionInfo   
        raise(e) 

def getSimpleDate (oriDateStr):
    try:
        dateArray = oriDateStr.split(' ')
        dateStr = dateArray[0].replace('-','')
        return dateStr 
    except Exception as e:   
        raise(e)   

def getSimpleTime(oriTimeStr):
    if ' ' in oriTimeStr :            
        timeArray = oriTimeStr.split(' ')
        timeStr = timeArray[1].replace(':','').split('.')[0]
    else:
        timeStr = "150000"
    return timeStr   
def getYearMonthDay(oriDate):
    try:
        year = oriDate / 10000
        month = (oriDate - year * 10000) / 100
        day = oriDate - year * 10000 - month * 100
        return (year, month, day)
    except Exception as e:  
        raise(e)   

def addOneDay(oriDate):
    year, month, day = getYearMonthDay(oriDate)
    day = day + 1
    if year % 4 == 0:
        monthArray = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        monthArray = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if day > monthArray[month-1]:
        day = 1
        month = month + 1
        if month > 12:
            month = 1
            year = year + 1
    addedDate = year * 10000 + month * 100 + day 
    return addedDate

def minusOneDay(oriDate):
    try:
        year, month, day = getYearMonthDay(oriDate)
        if year % 4 == 0:
            monthArray = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            monthArray = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        day = day - 1
        if day == 0:
            month = month - 1
            if month == 0:
                month = 12
                day = monthArray[month-1]
                year = year - 1
            else:
                day = monthArray[month-1]
        addedDate = year * 10000 + month * 100 + day 
        return addedDate
    except Exception as e: 
        raise(e)   

def getDateNow(data_type):
    curDate = datetime.datetime.now().strftime('%Y%m%d')
    curHourTime = float(datetime.datetime.now().strftime('%H'))
    curMinuTime = float(datetime.datetime.now().strftime('%M'))
    date = float(curDate)

    if "MarketData" in data_type and "day" not in data_type and "month" not in data_type and "week" not in data_type :
        leftday = (curHourTime * 60 + curMinuTime)/ (24 * 60)
        date += leftday
    else:
        date = int(curDate) 
        if curHourTime < 15:
            date = int(minusOneDay(date))
            date = float(date) + 0.99
    return date

def getpercenttime(time):
    hour = int(time) / 10000
    minu = int(time) % 10000 / 100
    time = float(hour * 60 + minu) / (24 * 60)
    return time

def trans_code_to_windstyle(oricode):
    wind_code = str(oricode)
    while len(wind_code) < 6:
        wind_code = '0' + wind_code
    if wind_code.startswith('6'):
        wind_code += '.SH'
    else:
        wind_code += '.SZ'
    return wind_code

def get_indexcode(style="ori"):
    indexCodeArray = []
    if style == "wind":
        indexCodeArray = ["000300.SH", "000016.SH", "000852.SH", \
                          "000904.SH", "000905.SH", "000906.SH", "399903.SZ"]
    elif style == "tinysoft":
        indexCodeArray = ["SH000300", "SH000016", "SH000852", \
                          "SH000904", "SH000905", "SH000906", "SZ399903"]
    else:
        indexCodeArray = ["000300", "000016", "000852", \
                          "000904", "000905", "000906", "399903"]
    return indexCodeArray

def get_filename_array(dirname):
    file_name = os.listdir(dirname)
    return file_name

def isTradingRest():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))     
     am_starttime = 93000
     am_endtime = 113020
     pm_starttime = 130000
     pm_endtime = 150020
     if wsq_time > am_endtime and wsq_time < pm_starttime:
         print wsq_time
         print 'Rest'
         return True
     else:
         return False

def isTradingOver():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))     
     am_starttime = 93000
     am_endtime = 113020
     pm_starttime = 130000
     pm_endtime = 150020
     if wsq_time > pm_endtime:
         print wsq_time
         print "Over"
         return True
     else:
         return False

def isTradingStart():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))
    #  print wsq_time
     am_starttime = 93000
     am_endtime = 113020
     pm_starttime = 130000
     pm_endtime = 150020
     if wsq_time > am_starttime:
         return True
     else:
         print "Too early"
         return False    