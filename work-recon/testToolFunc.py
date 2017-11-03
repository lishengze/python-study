# -*- coding: UTF-8 -*-
import threading
from multiprocessing import cpu_count
import datetime

from CONFIG import *
from databaseClass import MSSQL
from toolFunc import *
from databaseFunc import *
from netdataFunc import *

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
    integerDate = getIntegerDateNow(g_logFile)
    print type(integerDate)
    print integerDate