# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math
import sys

from CONFIG import *
from toolFunc import *

reload(sys)
sys.setdefaultencoding('utf-8')

class TinySoft(object):
    '''
    Connect TinySoft Platform
    '''
    def __init__(self):
        self.__name__ = "TinySoft"
        self.conn = ""
        self.curs = ""
        self.start_connect()

    def __del__(self):
        self.close_connect()
        # print '__del__'

    def start_connect(self, dataSource = "dsn=t1"):
        self.conn = pyodbc.connect(dataSource)
        self.curs = self.conn.cursor()   

    def close_connect(self):
        self.curs.close()
        self.conn.close()
        # print 'tinysoft_close_connect'

    def test_tsl(self, tsl_str):
        self.curs.execute(tsl_str)
        return self.curs.fetchall()

    def get_allA_secode(self):
        tsl_str = u"StockID:=getbk(\"A股\"); \n \
                   return StockID;"
        self.curs.execute(tsl_str)                
        result = self.curs.fetchall()
        transResult = []
        for data in result:
            transResult.append(data[0])
        return transResult   

    def get_Index_secode(self):
        indexCodeArray = ["SH000300", "SH000016", "SH000852", "SH000904", "SH000905", "SH000906", "SZ399903"]
        return indexCodeArray

    def getStartEndTime(self, oriStartTime, oriEndTime, tableDataStartTime, tableDataEndTime):
        timeArray = []
        if tableDataStartTime is None or tableDataEndTime is None:
            timeArray.append([oriStartTime, oriEndTime])
        else:
            if oriEndTime > getIntegerDateNow():
                oriEndTime = getIntegerDateNow()

            if tableDataEndTime > getIntegerDateNow():
                tableDataEndTime = getIntegerDateNow()

            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                startTime = addOneDay(tableDataEndTime)
                endTime = oriEndTime
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                endTime = minusOneDay(tableDataStartTime)
                timeArray.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                timeArray.append([oriStartTime, minusOneDay(tableDataStartTime)])
                timeArray.append([addOneDay(tableDataEndTime), oriEndTime])
        return timeArray