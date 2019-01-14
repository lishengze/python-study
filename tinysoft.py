import pyodbc
import traceback
import datetime
import threading
import math
import sys

from CONFIG import *
from func_tool import *
from func_secode import *

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

    def start_connect(self, dataSource = "dsn=t1"):
        try:
            self.conn = pyodbc.connect(dataSource)
            self.curs = self.conn.cursor() 
        except Exception as e:
            sleeptime = 60
            print("链接天软出错, %ds 后重连" % (sleeptime))
            time.sleep(sleeptime)
            self.start_connect()

    def close_connect(self):
        if type(self.curs) != 'str':            
            self.curs.close()

        if type(self.conn) != 'str':            
            self.conn.close()

    def test_tsl(self, tsl_str):
        self.curs.execute(tsl_str)
        return self.curs.fetchall()
        
    def get_tinysoft_a_market_secode_list(self):
        tsl_str = u"StockID:=getbk(\"A股\"); \n \
                   return StockID;"
        self.curs.execute(tsl_str)                
        result = self.curs.fetchall()
        transResult = []
        for data in result:
            transResult.append(data[0])
        return transResult   

    def get_market_secodelist(self, market_name):
        tsl_str = u'return  \n  \
                    Query("%s","",True,"","代码",DefaultStockID(), \n \
                    "名称",CurrentStockName());' % (market_name)
        self.curs.execute(tsl_str)                
        result = self.curs.fetchall()
        transResult = []
        for data in result:
            transResult.append([pure_secode(data[0]), data[1]])
        return transResult            

    def get_Index_secode(self):
        # indexCodeArray = ["SH000001", "SH000002", "SH000003", "SH000010", "SH000009",\
        #                   "SZ399001", "SZ399006", "SZ399005", "SZ399008", "SZ399102", "SZ399673", \
        #                   "SZ399101", "SZ399102", "SZ399106",  "SZ399107", "SZ399108", \
        #                   "SH000300", "SH000016", "SH000852", \
        #                   "SH000903", "SH000904", "SH000905", "SH000906", "SZ399903", \
        #                   'SH000908', 'SH000909', 'SH000910', 'SH000911', \
        #                   'SH000912', 'SH000913', 'SH000914','SH000951', 'SH000849', \
        #                   'SH000952', 'SH000915', 'SH000917']

        # indexCodeArray = ['SH000951', 'SH000849','SH000952']

        indexCodeArray = ['SH000903']

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