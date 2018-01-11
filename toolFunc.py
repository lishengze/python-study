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
    oriDate = int(oriDate)
    year = oriDate / 10000
    month = (oriDate - year * 10000) / 100
    day = oriDate - year * 10000 - month * 100
    return (year, month, day)

def getHourMinuSec(oriTime):
    time = int(oriTime)
    hour = time / 10000
    minute = (time - hour * 10000) / 100
    second = time - hour * 10000 - minute * 100
    return (hour, minute, second)

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
         print wsq_time, 'is rest time.\n'
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
         print wsq_time, " is over time.\n"
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
         print wsq_time, " is too early.\n"
         return False    

def print_data(msg, data):
    print "\n", msg, len(data)
    for item in data:
        print item

def is_time_equal(timea, timeb):
    if timea[0] == timeb[0] and timea[1] == timeb[1]:
        return True
    else:
        return False

def is_time_late(timea, timeb):
    if timea[0] < timeb[0]:
        return True
    elif timea[0] == timeb[0] and timea[1] < timeb[1]:
        return True
    else :
        return False

def is_time_early(timea, timeb):
    if timea[0] > timeb[0]:
        return True
    elif timea[0] == timeb[0] and timea[1] > timeb[1]:
        return True
    else :
        return False

def transto_tinytime(datetime):
    date = str(datetime[0])
    time = str(datetime[1])
    # year, month, day = getYearMonthDay(date)
    # hour, minute, second = getHourMinuSec(time)
    date_str = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    time_str = time[0:2] + ':' + time[2:4] + ':' + time[4:6]
    datetime_str = date_str + ' ' + time_str
    return datetime_str

def get_market_susdata(added_datetime, secode, close_price):
    appenddata = []
    appenddata.append(added_datetime)
    appenddata.append(secode)
    appenddata.append(close_price)
    appenddata.append(close_price)
    appenddata.append(close_price)
    appenddata.append(close_price)
    appenddata.append(0)
    appenddata.append(0)
    appenddata.append(close_price)

def add_suspdata_old(tradetime_array, ori_netdata):
    complete_data = []
    tradetime_index = 0
    for i in range(len(tradetime_array)):
        item = tradetime_array[i]
        if is_time_equal(item, [int(getSimpleDate(ori_netdata[0][0])), int(getSimpleTime(ori_netdata[0][0]))]):
            tradetime_index = i
            break                
    
    # print "tradetime_index: ", tradetime_index
    oridata_index = 0
    add_count = 0
    while tradetime_index < len(tradetime_array) and oridata_index < len(ori_netdata):
        cur_oridatetime = [int(getSimpleDate(ori_netdata[oridata_index][0])), int(getSimpleTime(ori_netdata[oridata_index][0]))]
        cur_tradetime = tradetime_array[tradetime_index]

        if is_time_late(cur_tradetime, cur_oridatetime):
            # print tradetime_index, cur_tradetime, oridata_index, cur_oridatetime
            added_datetime = transto_tinytime(cur_tradetime)
            # print "added_datetime: " , added_datetime
            secode = ori_netdata[oridata_index][1]
            close_price = ori_netdata[oridata_index-1][3]
            appenddata = get_market_susdata(added_datetime, secode, close_price)
            ori_netdata.insert(oridata_index, appenddata)
            add_count += 1

        oridata_index = oridata_index + 1
        tradetime_index = tradetime_index + 1

    while tradetime_index < len(tradetime_array):
        cur_tradetime = tradetime_array[tradetime_index]
        added_datetime = transto_tinytime(cur_tradetime)
        secode = ori_netdata[oridata_index-1][1]
        close_price = ori_netdata[oridata_index-1][3]
        appenddata = get_market_susdata(added_datetime, secode, close_price)
        ori_netdata.insert(oridata_index, appenddata)

        tradetime_index += 1
        oridata_index += 1
        add_count += 1

    # print "add_count: ", add_count    
    complete_data = ori_netdata
    return complete_data

def add_suspdata(tradetime_array, ori_netdata, isfirstInterval=False, latest_data=[]):
    complete_data = []
    tradetime_index = 0
    if isfirstInterval:
        for i in range(len(tradetime_array)):
            item = tradetime_array[i]
            if is_time_equal(item, [int(getSimpleDate(ori_netdata[0][0])), int(getSimpleTime(ori_netdata[0][0]))]):
                tradetime_index = i
                break                
    
    # print "tradetime_index: ", tradetime_index
    oridata_index = 0
    add_count = 0
    while tradetime_index < len(tradetime_array) and oridata_index < len(ori_netdata):
        cur_oridatetime = [int(getSimpleDate(ori_netdata[oridata_index][0])), int(getSimpleTime(ori_netdata[oridata_index][0]))]
        cur_tradetime = tradetime_array[tradetime_index]

        if is_time_late(cur_tradetime, cur_oridatetime):
            # print tradetime_index, cur_tradetime, oridata_index, cur_oridatetime
            added_datetime = transto_tinytime(cur_tradetime)
            # print "added_datetime: " , added_datetime
            if oridata_index == 0:
                secode = latest_data[1]
                close_price = latest_data[3]
            else:
                secode = ori_netdata[oridata_index][1]
                close_price = ori_netdata[oridata_index-1][3]

            appenddata = get_market_susdata(added_datetime, secode, close_price)
            ori_netdata.insert(oridata_index, appenddata)
            add_count += 1

        oridata_index = oridata_index + 1
        tradetime_index = tradetime_index + 1

    while tradetime_index < len(tradetime_array):
        cur_tradetime = tradetime_array[tradetime_index]
        added_datetime = transto_tinytime(cur_tradetime)
        if oridata_index == 0:
            secode = latest_data[1]
            close_price = latest_data[3]
        else:
            secode = ori_netdata[oridata_index][1]
            close_price = ori_netdata[oridata_index-1][3]
        appenddata = get_market_susdata(added_datetime, secode, close_price)
        ori_netdata.insert(oridata_index, appenddata)

        tradetime_index += 1
        oridata_index += 1
        add_count += 1

    # print "add_count: ", add_count    
    complete_data = ori_netdata
    return complete_data

def get_time_array(ori_netdata):
    time_array = []
    for item in ori_netdata:
        time_array.append([int(getSimpleDate(item[0])), int(getSimpleTime(item[0]))])
    return time_array

def get_missing_time_array(complete_time_array, ori_time_array):
    missing_time_array = []

    complete_time_index = 0
    while complete_time_index < len(complete_time_array) and \
          is_time_equal(complete_time_array[complete_time_index], ori_time_array[0]) :
          complete_time_index += 1

    while complete_time_index < len(complete_time_array):
        item = complete_time_array[complete_time_index]
        if item not in ori_time_array:
            missing_time_array.append(item)
        complete_time_index += 1

    return missing_time_array