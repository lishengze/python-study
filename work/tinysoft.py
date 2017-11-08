# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from CONFIG import *
from toolFunc import *

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

    # def record_with_rock(self, info):
    #     self.file_lock.acquire()
    #     self.log_file.write(info + "\n")
    #     print(info)
    #     self.file_lock.release()        

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