# -*- coding: UTF-8 -*-
import math

import os
import traceback
import threading
import pyodbc
import datetime

from databaseClass import MSSQL
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
    try:
        timeArray = oriTimeStr.split(' ')
        timeStr = timeArray[1].replace(':','').split('.')[0]
        return timeStr   
    except Exception as e:
        raise(e)  

def getYearMonthDay(oriDate):
    try:
        year = oriDate / 10000
        month = (oriDate - year * 10000) / 100
        day = oriDate - year * 10000 - month * 100
        return (year, month, day)
    except Exception as e:  
        raise(e)   

def addOneDay(oriDate):
    try:
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
    except Exception as e:   
        raise(e)   

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

def getIntegerDateNow():
    try:
        curDate = datetime.datetime.now().strftime('%Y%m%d')
        curHourTime = datetime.datetime.now().strftime('%H')
        curDate = long(curDate)
        if long(curHourTime) < 15:
            curDate = minusOneDay(curDate)
        integerDate = long(curDate)
        return integerDate
    except Exception as e:
        raise(e)   