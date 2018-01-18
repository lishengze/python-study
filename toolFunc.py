# -*- coding: UTF-8 -*-
import math

import os
import traceback
import threading
import pyodbc
import datetime
import math
from operator import itemgetter, attrgetter
from CONFIG import *

import time


import datetime
import threading

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
        # indexCodeArray = ["SH000300"]                          
    else:
        indexCodeArray = ["000300", "000016", "000852", \
                          "000904", "000905", "000906", "399903"]
    return indexCodeArray

def get_filename_array(dirname):
    file_name = os.listdir(dirname)
    return file_name

def is_minute_type(data_type):
    if "m" in data_type and "month" not in data_type:
        return True
    else:
        return False

def is_minute_data(time_data):
    if int(getSimpleTime(time_data)) != 150000:
        return True
    else:
        return False

def isTradingRest():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))     
     am_starttime = 93000
     am_endtime = 113003
     pm_starttime = 130000
     pm_endtime = 150003
     if wsq_time > am_endtime and wsq_time < pm_starttime:
         print wsq_time, 'is rest time.\n'
         return True
     else:
         return False

def isTradingOver():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))     
     am_starttime = 93000
     am_endtime = 113003
     pm_starttime = 130000
     pm_endtime = 150003
     if wsq_time > pm_endtime:
         print wsq_time, " is over time.\n"
         return True
     else:
         return False

def isTradingStart():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))
    #  print wsq_time
     am_starttime = 93000
     am_endtime = 113003
     pm_starttime = 130000
     pm_endtime = 150003
     if wsq_time > am_starttime:
         return True
     else:
         print wsq_time, " is too early.\n"
         return False    

def print_data(msg, data):
    print "\n", msg, len(data)
    if len(data) > 50:
        data = data[0:50]

    for item in data:
        print item

def print_dict_data(msg, data):
    print "\n", msg, len(data)
    for item in data:
        print item,": ", data[item]

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

def trans_floattime_to_datetime(floattime):
    pass

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
    return appenddata

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

def add_suspdata_oldb(tradetime_array, ori_netdata, isfirstInterval=False, latest_data=[]):
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

def add_suspdata(tradetime_array, ori_netdata, isfirstInterval=False, latest_data=[]):
    complete_data = []
    tradetime_index = 0
    if isfirstInterval:
        if len(ori_netdata) == 0 or (len(ori_netdata) == 1 and is_minute_data(ori_netdata[0][0])):
            return ori_netdata
        else:
            i = 0
            while i < len(tradetime_array):
                item = tradetime_array[i]
                if is_time_equal(item, [int(getSimpleDate(ori_netdata[0][0])), int(getSimpleTime(ori_netdata[0][0]))]):
                    tradetime_index = i
                    break  
                i += 1

    oridata_index = 0
    add_count = 0
    print "Start: tradetime_index: ", tradetime_index, ", isfirstInterval: ", isfirstInterval

    while tradetime_index < len(tradetime_array) and oridata_index < len(ori_netdata):
        cur_oridatetime = [int(getSimpleDate(ori_netdata[oridata_index][0])), int(getSimpleTime(ori_netdata[oridata_index][0]))]
        cur_tradetime = tradetime_array[tradetime_index]

        if is_time_late(cur_tradetime, cur_oridatetime):
            # print tradetime_index, cur_tradetime, oridata_index, cur_oridatetime
            added_datetime = transto_tinytime(cur_tradetime)
            # print "oridata_index: ", oridata_index, ori_netdata[oridata_index-1]
            if oridata_index == 0:
                print "tradetime_index: ", tradetime_index, ", oridata_index: ", oridata_index, ", dataNumb: ", len(ori_netdata)
                print "cur_tradetime: ", cur_tradetime, ", cur_oridatetime: ", cur_oridatetime
                secode = latest_data[2]
                close_price = latest_data[3]
            else:
                secode = ori_netdata[oridata_index][1]
                close_price = ori_netdata[oridata_index-1][3]
            
            appenddata = get_market_susdata(added_datetime, secode, close_price)
            # print "appenddata, ", appenddata
            ori_netdata.insert(oridata_index, appenddata)
            add_count += 1

        oridata_index = oridata_index + 1
        tradetime_index = tradetime_index + 1

    print "End: tradetime_index: ", tradetime_index, ", oridata_index: ", oridata_index
    while tradetime_index < len(tradetime_array):
        cur_tradetime = tradetime_array[tradetime_index]
        added_datetime = transto_tinytime(cur_tradetime)
        secode = ""
        close_price = 0
        if oridata_index == 0:
            secode = latest_data[2]
            close_price = latest_data[3]
        else:
            secode = ori_netdata[oridata_index-1][1]
            close_price = ori_netdata[oridata_index-1][3]
        appenddata = get_market_susdata(added_datetime, secode, close_price)
        ori_netdata.insert(oridata_index, appenddata)

        tradetime_index += 1
        oridata_index += 1
        add_count += 1

    print "add_count: ", add_count    
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

def get_tradetime_byindex_interval(netconn_obj, database_obj, source_conditions):
    starttime = source_conditions[0]
    endtime = source_conditions[1]
    tablename_array = netconn_obj.get_Index_secode()
    source = netconn_obj.get_index_source_info(source_conditions)

    tradetime_array = []
    tradetime_count = 10
    for i in range(tradetime_count):
        tradetime_array.append([])

    # database_obj.clearDatabase()
    database_obj.completeDatabaseTable(tablename_array)

    for table_name in tablename_array:
        cur_source = netconn_obj.get_cursource(table_name, source)
        trans_conditions = database_obj.get_transed_conditions(table_name, cur_source)
        print "trans_conditions.size: ", len(trans_conditions)
        # print "table_name: ", table_name,",  trans_conditions: ", trans_conditions
        for i in range(len(trans_conditions)):
            cur_condition = trans_conditions[i]
            ori_netdata = netconn_obj.get_netdata(cur_condition)       
            # print "cur_condition: ", cur_condition , ", datanumb: ", len(ori_netdata)                 
            for item in ori_netdata:
                datetime = [int(getSimpleDate(item[0])), int(getSimpleTime(item[0]))]
                if datetime not in tradetime_array[i]:
                    tradetime_array[i].append(datetime)

    print_data("tradetime_array: ", tradetime_array)
    return tradetime_array

def get_tradetime_byindex(netconn_obj, database_obj, source_conditions):
    starttime = source_conditions[0]
    endtime = source_conditions[1]
    tablename_array = netconn_obj.get_Index_secode()
    source = netconn_obj.get_index_source_info(source_conditions)
    tradetime_array = []

    # database_obj.clearDatabase()
    database_obj.completeDatabaseTable(tablename_array)

    for table_name in tablename_array:
        cur_source = netconn_obj.get_cursource(table_name, source)
        trans_conditions = database_obj.get_transed_conditions(table_name, cur_source)
        print "trans_conditions.size: ", len(trans_conditions)
        # print "table_name: ", table_name,",  trans_conditions: ", trans_conditions
        for cur_condition in trans_conditions:
            ori_netdata = netconn_obj.get_netdata(cur_condition)       
            print "cur_condition: ", cur_condition , ", datanumb: ", len(ori_netdata)                 
            for item in ori_netdata:
                datetime = [int(getSimpleDate(item[0])), int(getSimpleTime(item[0]))]
                if datetime not in tradetime_array:
                    print datetime
                    tradetime_array.append(datetime)

    print_data("tradetime_array: ", tradetime_array)
    return tradetime_array

def get_index_tradetime(netconn_obj, starttime, endtime):
    # tablename_array = get_indexcode(style="tinysoft")
    tablename_array = ["SH000300", "SH000016"]
    tradetime_array = []

    for table_name in tablename_array:
        condition = [table_name, starttime, endtime]
        ori_netdata = netconn_obj.get_netdata(condition)
        print table_name, " dataNumb: ", len(ori_netdata)
        for item in ori_netdata:
            datetime = [int(getSimpleDate(item[0])), int(getSimpleTime(item[0]))]
            if datetime not in tradetime_array:
                tradetime_array.append(datetime)     

    return tradetime_array   

def get_detail_time(minutes):
    minutes = minutes * 24 * 60
    hour = int(minutes / 60)
    minu = int(minutes - hour*60)
    time = hour * 10000 + minu * 100
    return time

def get_sub_index_tradetime(complete_tradetime, startdate, enddate, starttime=93100, endtime=150000):
    if float(startdate) - int(startdate) != 0:
        starttime = get_detail_time(float(startdate) - int(startdate))
        # print "starttime: ", starttime

    if float(enddate) - int(enddate) != 0:
        endtime = get_detail_time(float(enddate) - int(enddate))
        # print "endtime: ", endtime

    # print 'startdate: ', int(startdate), ', starttime: ', int(starttime)
    # print 'enddate: ', int(enddate), ', endtime: ', int(endtime)

    start_index = 0
    end_index = len(complete_tradetime) -1
    while start_index < len(complete_tradetime) \
        and int(complete_tradetime[start_index][0]) < int(startdate):
        start_index += 1

    while start_index < len(complete_tradetime) \
        and int(complete_tradetime[start_index][1]) < int(starttime):
        start_index += 1

    while end_index > -1 and int(complete_tradetime[end_index][0] > int (enddate)):
        end_index -= 1


    while end_index > -1 and int(complete_tradetime[end_index][1] > int (endtime)) \
    and int(complete_tradetime[end_index][0] == int (enddate)):
        end_index -= 1

    # print "start_index: ", start_index, ", end_index: ", end_index
    return complete_tradetime[start_index:end_index+1]

def cmp_net_time(oritimea, oritimeb):
    timea = [int(getSimpleDate(oritimea)), int(getSimpleTime(oritimea))]
    timeb = [int(getSimpleDate(oritimeb)), int(getSimpleTime(oritimeb))]

    # print "oritimea: ", oritimea ,", timea: ", timea
    # print "oritimeb: ", oritimeb ,", timeb: ", timeb
    # print timea, timeb, is_time_late(timea, timeb)

    if is_time_late(timea, timeb):
        return -1
    if is_time_equal(timea, timeb):
        return 0
    if is_time_early(timea, timeb):
        return 1

def cmp_database_time(timea, timeb):
    if is_time_late(timea, timeb):
        return -1
    if is_time_equal(timea, timeb):
        return 0
    if is_time_early(timea, timeb):
        return 1

def get_restore_info(secode, ori_netdata, latestdata=[], firstdata=[]):
    ori_netdata.sort(cmp=cmp_net_time, key=itemgetter(0)) 
    restore_data = []

    if len(ori_netdata) <2:
        return restore_data

    if len(firstdata)!= 0:
        i = len(ori_netdata) - 2
        ori_time = [int(getSimpleDate(ori_netdata[i][0])), int(getSimpleTime(ori_netdata[i][0]))]
        first_time = [firstdata[0], firstdata[1]]
        yclose = float(firstdata[10])
        close = float(ori_netdata[i][3])
        if  yclose != close and is_time_late(ori_time, first_time):
            print "firstdata: ", firstdata
            print "ori_nedata["+ str(i) +"]: ", ori_netdata[i]
            restore_data.append(secode)
            restore_data.append(firstdata[0])
            restore_data.append(firstdata[1])
    else:
        i = len(ori_netdata) - 1
    
    while i > 0 and len(restore_data) == 0:
        if ori_netdata[i][8] != ori_netdata[i-1][3]:
            restore_data.append(secode)
            restore_data.append(int(getSimpleDate(ori_netdata[i][0])))
            restore_data.append(int(getSimpleTime(ori_netdata[i][0])))
            break
        i -= 1

    if len(restore_data) == 0 and len(latestdata) != 0 :
        ori_time = [int(getSimpleDate(ori_netdata[i][0])), int(getSimpleTime(ori_netdata[i][0]))]
        lastest_time = [latestdata[0], latestdata[1]]

        if float(ori_netdata[i][8]) != float(latestdata[4]) and \
            is_time_late(lastest_time, ori_time):
            print "ori_nedata["+ str(i) +"]: ", ori_netdata[i]
            print "latestdata: ", latestdata
            restore_data.append(secode)
            restore_data.append(int(getSimpleDate(ori_netdata[i][0])))
            restore_data.append(int(getSimpleTime(ori_netdata[i][0])))
    return restore_data

def compute_restore_data(sort_data):
    sort_data = list(sort_data)
    i = len(sort_data) - 1
    while i > 0:
        sort_data[i] = list(sort_data[i])
        sort_data[i-1] = list(sort_data[i-1])
        sort_data[i-1][2] = sort_data[i][2] / (1 + sort_data[i][3])
        sort_data[i][4] = sort_data[i-1][2]
        i -= 1

    sort_data[i] = list(sort_data[i])
    sort_data[i][4] = sort_data[i][2] / (1 + sort_data[i][3])
    return sort_data

def get_restore_time_list(ori_restore_data):
    restore_time_array = []
    for item in ori_restore_data:
        if len(ori_restore_data) == 3:
            if [item[1], item[2]] not in restore_time_array:
                restore_time_array.append([item[1], item[2]])
    return restore_time_array