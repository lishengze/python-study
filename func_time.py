import math

import os
import traceback
import threading
import pyodbc
import datetime
import math
from operator import itemgetter, attrgetter
from CONFIG import *

from func_qt import update_tableinfo

import time
import threading

def getTime(intTime):
    hour, minute, second = getHourMinuSec(intTime)
    return  datetime.time(hour, minute, second)

def getDate(intDate):
    year, month, day = getDateList(intDate)
    return datetime.datetime(int(year), int(month), int(day), 0,0,0)

def getDateList(intDate):
    year = str( math.floor(intDate / 10000))
    intDate = intDate % 10000
    month = str(math.floor(intDate / 100))
    intDate = intDate % 100
    day = str(intDate)
    return [year, month, day]

def transto_wind_datetime(intDate):
    date_list = getDateList(intDate)
    str_date = '-'.join(date_list)
    return str_date
    
def getSimpleDate(oriDateStr):
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
    year = int(oriDate / 10000)
    month = int((oriDate - year * 10000) / 100)
    day = int(oriDate - year * 10000 - month * 100)
    return (year, month, day)

def getHourMinuSec(oriTime):
    time = int(oriTime)
    hour = int(time / 10000)
    minute = int((time - hour * 10000) / 100)
    second = int(time - hour * 10000 - minute * 100)
    return (hour, minute, second)

def addOneDay(oriDate):
    year, month, day = getYearMonthDay(oriDate)
    # print (year, month, day)
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

def getDateNow():
    curDate = datetime.datetime.now().strftime('%Y%m%d')
    curHourTime = float(datetime.datetime.now().strftime('%H'))
    date = float(curDate)

    date = int(curDate) 
    if curHourTime < 15:
        date = int(minusOneDay(date))
    return date

def getDateNow_percent(data_type):
    curDate = datetime.datetime.now().strftime('%Y%m%d')
    curHourTime = float(datetime.datetime.now().strftime('%H'))
    curMinuTime = float(datetime.datetime.now().strftime('%M'))
    date = float(curDate)

    date = int(curDate) 
    if curHourTime < 15:
        date = int(minusOneDay(date))
        date = float(date) + 0.99

    if "MarketData" in data_type and "day" not in data_type and "month" not in data_type and "week" not in data_type :
        leftday = (curHourTime * 60 + curMinuTime)/ (24 * 60)
        date += leftday
    else:
        date = int(curDate) 
        if curHourTime < 15:
            date = int(minusOneDay(date))
            # date = float(date) + 0.99
    return date

def getpercenttime(time):
    hour = int(int(time) / 10000)
    minu = int(int(time) % 10000 / 100)
    time = float(hour * 60 + minu) / (24 * 60)
    return time

def get_time_key(data):
    int_date = int((data))
    int_time = int((data))
    int_datetime = int_date*100000000 + int_time
    return int_datetime
    
def is_time_equal(timea, timeb):
    if timea[0] == timeb[0] and timea[1] == timeb[1]:
        return True
    else:
        return False

def is_time_late(timea, timeb):
    '''
    time: [date, time]
    timeb 晚于 timea
    '''
    if timea[0] < timeb[0]:
        return True
    elif timea[0] == timeb[0] and timea[1] < timeb[1]:
        return True
    else :
        return False

def is_time_early(timea, timeb):
    '''
    time: [date, time]
    timeb 早于 timea
    '''
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

def get_time_array(ori_netdata):
    time_array = []
    for item in ori_netdata:
        time_array.append([int((item[0])), int((item[0]))])
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
        print ("trans_conditions.size: ", len(trans_conditions))
        # print "table_name: ", table_name,",  trans_conditions: ", trans_conditions
        for i in range(len(trans_conditions)):
            cur_condition = trans_conditions[i]
            ori_netdata = netconn_obj.get_netdata(cur_condition)       
            # print "cur_condition: ", cur_condition , ", datanumb: ", len(ori_netdata)                 
            for item in ori_netdata:
                datetime = [int((item[0])), int((item[1]))]
                if datetime not in tradetime_array[i]:
                    tradetime_array[i].append(datetime)

    # print_data("tradetime_array: ", tradetime_array)
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
        print ("trans_conditions.size: ", len(trans_conditions))
        # print "table_name: ", table_name,",  trans_conditions: ", trans_conditions
        for cur_condition in trans_conditions:
            ori_netdata = netconn_obj.get_netdata(cur_condition)       
            print ("cur_condition: ", cur_condition , ", datanumb: ", len(ori_netdata))              
            for item in ori_netdata:
                datetime = [int((item[0])), int((item[1]))]
                if datetime not in tradetime_array:
                    print (datetime)
                    tradetime_array.append(datetime)

    # print_data("tradetime_array: ", tradetime_array)
    return tradetime_array

def get_index_tradetime(netconn_obj, starttime, endtime):
    # tablename_array = get_indexcode(style="tinysoft")
    # tablename_array = ["SH000300", "SH000016"]
    tablename_array = ["SH000300"]
    tradetime_array = []

    for table_name in tablename_array:
        condition = [table_name, starttime, endtime]
        ori_netdata = netconn_obj.get_netdata(condition)
        print (table_name, " dataNumb: ", len(ori_netdata))
        for item in ori_netdata:
            datetime = [int(item[0]), int(item[1])]
            if datetime not in tradetime_array:
                tradetime_array.append(datetime)     

    print ('\n')
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
    timea = [int((oritimea)), int((oritimea))]
    timeb = [int((oritimeb)), int((oritimeb))]

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

def is_minute_type(data_type):
    if "m" in data_type and "month" not in data_type:
        return True
    else:
        return False

def is_minute_data(time_data):
    if int((time_data)) != 150000:
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
         print (wsq_time, 'is rest time.\n')
         return True
     else:
         print (wsq_time, ' is trade time.')
         return False

def isTradingOver():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))     
     am_starttime = 93000
     am_endtime = 113003
     pm_starttime = 130000
     pm_endtime = 150003
     if wsq_time > pm_endtime:
         print (wsq_time, " is over time.\n")
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
         print (wsq_time, " is too early.\n")
         return False    

def isAnnouncementOver():
     wsq_time = int(datetime.datetime.now().strftime("%H%M%S"))     
     an_endtime = 170000
     if wsq_time > an_endtime:
         print (wsq_time, " is over time.\n")
         return True
     else:
         return False    

def get_next_trading_day(ori_date):
    next_date = ori_date + datetime.timedelta(1)    
    while isTradingDay(next_date) == False:
        next_date = next_date + datetime.timedelta(1)
    return next_date

def isTradingDay(datetime):
    specialNoTradingDay = [20181230, 20181231, 20180101, \
                           20180215, 20180216, 20180217, 20180218, 20180219, 20180220, 20180221, \
                           20180405, 20180406, 20180407, \
                           20180420, 20180430, 20180501, \
                           20180616, 20180617, 20180618, \
                           20180922, 20180923, 20180924, \
                           20181001, 20181002, 20181003, 20181004, 20181005, 20181006, 20181007]
    intDate = int(datetime.strftime('%Y%m%d'))
    dayOfWeek = datetime.date().isoweekday()
    if dayOfWeek > 5 or intDate in specialNoTradingDay:
        return False
    else:
        return True

def wait_today_histdata_time(table_view = None, datatype="MarketData"):
    if "MarketData" in datatype:
        start_minute = 30
    else:
        start_minute = 15
    curDateTime = datetime.datetime.now()
    work_start_time = datetime.datetime(curDateTime.year, curDateTime.month, curDateTime.day,\
                                        15, start_minute, 0)
    
    sleep_seconds = (work_start_time - curDateTime).total_seconds()
    print('curDateTime: %s, work_start_time: %s, sleep_seconds: %d' % \
            (curDateTime.strftime('%Y-%m-%d %H:%M:%S'),  work_start_time.strftime('%Y-%m-%d %H:%M:%S'), sleep_seconds))

    if sleep_seconds > 0:
        update_tableinfo(table_view, '等到%s, 开始更新今天的最新数据' %\
                         (work_start_time.strftime('%H:%M:%S')))
        time.sleep(sleep_seconds)
        return True
    else:
        return False
         
def wait_nexttradingday_histdata_time(table_view = None, datatype="MarketData"):
    curDateTime = datetime.datetime.now()
    nextTradingDay = curDateTime + datetime.timedelta(1)

    while not isTradingDay(nextTradingDay):
        nextTradingDay = nextTradingDay + datetime.timedelta(1)

    if "MarketData" in datatype:
        start_minute = 30
    else:
        start_minute = 15

    nextTradingDayTime = datetime.datetime(nextTradingDay.year, \
                                            nextTradingDay.month, \
                                            nextTradingDay.day,\
                                            15, start_minute, 0)

    wait_secs = (nextTradingDayTime - curDateTime).total_seconds()

    print('curDateTime: %s, nextTradingDayTime: %s, wait_secs: %d' % \
            (curDateTime.strftime('%Y-%m-%d %H:%M:%S'),  nextTradingDayTime.strftime('%Y-%m-%d %H:%M:%S'), wait_secs))

    update_tableinfo(table_view, '当天数据更新完成，等到%s再更新数据' %\
                     (nextTradingDayTime.strftime('%Y-%m-%d %H:%M:%S')))
    time.sleep(wait_secs)

def waitForNextTradingDay():
    curDateTime = datetime.datetime.now()
    waitDays = -1
    if not isTradingDay(curDateTime):
        dayOfWeek = curDateTime.date().isoweekday() 
        if dayOfWeek > 5:
            waitDays = 8 - dayOfWeek
        else:
            waitDays = 1
    elif isTradingOver():
        print ("Today's trading is over.")
        if dayOfWeek >= 5:
            waitDays = 8 - dayOfWeek
        else:
            waitDays = 1

    if waitDays != -1:
        waitDays = datetime.timedelta(waitDays)
        nextTradingDay = curDateTime + waitDays
        

        nextTradingDayTime = datetime.datetime(nextTradingDay.year, \
                                               nextTradingDay.month, \
                                               nextTradingDay.day,\
                                               8,0,0)

        waitSecs = (nextTradingDayTime - curDateTime).total_seconds()
        print ("nextTradingDayTime: ", nextTradingDayTime, ", waitSecs: ", waitSecs)
        # time.sleep(waitSecs)
    else:
        # print "Don't need to wait!"
        pass

def waitForNextDay(table_view=None):
    curDateTime = datetime.datetime.now()
    waitDays = datetime.timedelta(1)
    nextTradingDay = curDateTime + waitDays    

    nextTradingDayTime = datetime.datetime(int(nextTradingDay.strftime('%Y')), \
                                           int(nextTradingDay.strftime('%m')), \
                                           int(nextTradingDay.strftime('%d')),\
                                           8,0,0)

    waitSecs = (nextTradingDayTime - curDateTime).total_seconds()
    msg = "新的公告下载时间为: %s, 等待 %d 秒" %(nextTradingDayTime.strftime('%Y-%m-%d %H:%M:%S'), waitSecs)
    print (msg)
    if table_view != None:
        update_tableinfo(table_view, msg)
    time.sleep(waitSecs)

def get_trade_start_minute(curr_time):
    hour, minute, secode = getHourMinuSec(curr_time)
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    curr_datetime = datetime.datetime(year, month, day, hour, minute, secode)
    am_start_time = datetime.datetime(year, month, day, 9, 30, 0)
    pm_start_time = datetime.datetime(year, month, day, 13, 0, 0)

    delta_minute = -1

    if curr_datetime > pm_start_time:
        delta_minute = int((curr_datetime - pm_start_time).total_seconds() / 60)
    elif curr_datetime > am_start_time:
        delta_minute = int((curr_datetime - am_start_time).total_seconds() / 60)

    return delta_minute
        
    
