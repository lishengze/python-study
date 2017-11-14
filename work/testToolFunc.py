# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime
import math

from CONFIG import *
from toolFunc import *


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
    data_type = 'WeightData'
    integerDate = getIntegerDateNow(data_type)
    print type(integerDate)
    print integerDate
    print math.ceil(integerDate)
    print int(integerDate)

if __name__ == '__main__':
    testGetIntegerDateNow()