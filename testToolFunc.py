# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import math

from CONFIG import *
from func_tool import *
from excel import EXCEL


g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')

# def testDate():
#     oriDate = 20161201
#     print getYearMonthDay(oriDate, g_logFile)
#     addDate = addOneDay(oriDate, g_logFile)
#     print addDate
#     minusDate = minusOneDay(oriDate, g_logFile)
#     print minusDate

# def testGetIntegerDateNow():
#     data_type = 'MarketData'
#     # data_type = 'WeightData'
#     integerDate = getIntegerDateNow(data_type)
#     print type(integerDate)
#     print integerDate
#     print math.ceil(integerDate)
#     print int(integerDate)

# def test_get_filename_array():
#     dirname =  "D:/strategy"
#     print get_filename_array(dirname)

# def scan_excelfile():
#     global secodelist, dirname
#     filename_array = get_filename_array(dirname)
    
#     for filename in filename_array:
#         complete_filename = dirname + '/' + filename
#         excelobj = EXCEL(complete_filename)
#         tmp_secodelist = excelobj.get_data_byindex()
#         for code in tmp_secodelist:
#             transcode = trans_code_to_windstyle(code)
#             if transcode not in secodelist:
#                 secodelist.append(transcode)
    
#     print secodelist
#     timer = threading.Timer(timeInterval, scan_excelfile, )
#     timer.start();

# def get_secodelist():
#     global secodelist, dirname, timeInterval
#     timeInterval = 2
#     dirname =  "D:/strategy"
#     secodelist = get_index_code_list(style="wind")

#     timer = threading.Timer(timeInterval, scan_excelfile, )
#     timer.start();
    
# def testTradingTime():
#     isTradingRest()
#     isTradingOver()

# def test_transto_tinytime():
#     datetime = [20171226, 110000]
#     print transto_tinytime(datetime)

# def test_getdatabase_tablename():
#     database_name = "MarketData_1m"
#     tablename_array = get_database_tablename(database_name)
#     print "tablename_array: ", tablename_array

# def test_sortdata():
#     oridata = [['2017-01-11 9:31:00', 1], ["2017-01-11 9:32:00", 2], \
#                 ["2017-01-10 9:31:00", 3], ["2017-01-10 8:32:00", 4],\
#                 ["2017-01-19 9:31:00", 5], ["2017-01-19 7:32:00", 6],\
#                 ["2017-01-13 9:31:00", 7], ["2017-01-13 15:32:00", 8],\
#                 ["2017-01-12 9:31:00", 9], ["2017-01-12 9:32:00", 10],\
#                 ["2017-01-20 15:31:00", 11], ["2017-01-20 9:32:00", 12]]

#     print_data("oridata: ", oridata)

#     sorted_data = get_restore_info("", oridata, [])
#     print_data("sorted_data: ", sorted_data)

# def test_split():
#     datestr = '2017-01-11 9:31:00'
#     date_array = datestr.split(' ')
#     print datestr, date_array
#     print getSimpleDate(datestr)

def test_new_sort():
    oridata = [['2017-01-11 9:31:00', 1], ["2017-01-11 9:32:00", 2], \
                ["2017-01-10 9:31:00", 3], ["2017-01-10 8:32:00", 4],\
                ["2017-01-19 9:31:00", 5], ["2017-01-19 7:32:00", 6],\
                ["2017-01-13 9:31:00", 7], ["2017-01-13 15:32:00", 8],\
                ["2017-01-12 9:31:00", 9], ["2017-01-12 9:32:00", 10],\
                ["2017-01-20 15:31:00", 11], ["2017-01-20 9:32:00", 12]]
    print_data("oridata: ", oridata)
    trans_data = []
    for tmpdata in oridata:
        trans_data.append(get_time_key(tmpdata[0]))
    # print_data("oritrans_datadata: ", trans_data)

    oridata.sort(key=lambda x: get_time_key(x[0]))
    print_data("oridata: ", oridata)

def test_trans_matrix():
    ori_data = [[1,2,3],[4,5,6], [7,8,9]]
    trans_data = trans_matrix(ori_data)
    print(ori_data)
    print(trans_data)

def test_create_array():
    array = create_array(0.01, 0.02, 0.10)
    print(array)

if __name__ == '__main__':
    # testGetIntegerDateNow()
    # test_get_filename_array()
    # get_secodelist()
    # testTradingTime()
    # test_transto_tinytime()
    # test_getdatabase_tablename()
    # test_sortdata()
    # test_split()
    # test_new_sort()
    # test_trans_matrix()
    test_create_array()