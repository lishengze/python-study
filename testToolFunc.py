# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import math

from CONFIG import *
from toolFunc import *
from excel import EXCEL


g_logFileName = 'log.txt'
g_logFile = open(g_logFileName, 'w')

def testDate():
    oriDate = 20161201
    print getYearMonthDay(oriDate, g_logFile)
    addDate = addOneDay(oriDate, g_logFile)
    print addDate
    minusDate = minusOneDay(oriDate, g_logFile)
    print minusDate

def testGetIntegerDateNow():
    data_type = 'MarketData'
    # data_type = 'WeightData'
    integerDate = getIntegerDateNow(data_type)
    print type(integerDate)
    print integerDate
    print math.ceil(integerDate)
    print int(integerDate)

def test_get_filename_array():
    dirname =  "D:/strategy"
    print get_filename_array(dirname)

def scan_excelfile():
    global secodelist, dirname
    filename_array = get_filename_array(dirname)
    
    for filename in filename_array:
        complete_filename = dirname + '/' + filename
        excelobj = EXCEL(complete_filename)
        tmp_secodelist = excelobj.get_data_byindex()
        for code in tmp_secodelist:
            transcode = trans_code_to_windstyle(code)
            if transcode not in secodelist:
                secodelist.append(transcode)
    
    print secodelist
    timer = threading.Timer(timeInterval, scan_excelfile, )
    timer.start();

def get_secodelist():
    global secodelist, dirname, timeInterval
    timeInterval = 2
    dirname =  "D:/strategy"
    secodelist = get_indexcode(style="wind")

    timer = threading.Timer(timeInterval, scan_excelfile, )
    timer.start();
    

if __name__ == '__main__':
    # testGetIntegerDateNow()
    # test_get_filename_array()
    get_secodelist()