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
    def __init__(self, log_file, file_lock):
        try:
            self.__name__ = "TinySoft"
            self.conn = ""
            self.curs = ""
            self.log_file = log_file
            self.file_lock = file_lock
            self.startConnect()
        except:
            exception_str = "[X]: Thread Name " + str(threading.currentThread().getName()) + '\n' \
                          + str(traceback.format_exc())
            self.record_with_rock(exception_str)
            raise(Exception(exception_str))

    def __del__(self):
        self.closeConnect()
        # print '__del__'

    def startConnect(self, dataSource = "dsn=t1"):
        self.conn = pyodbc.connect(dataSource)
        self.curs = self.conn.cursor()   
        # print 'tinysoft_start_connect'

    def closeConnect(self):
        self.curs.close()
        self.conn.close()
        # print 'tinysoft_close_connect'

    def record_with_rock(self, info):
        self.file_lock.acquire()
        self.log_file.write(info + "\n")
        print(info)
        self.file_lock.release()

    def getInsertStockDataStr(self, result, table_name):
        col_str = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
        TDATE = getSimpleDate(result[0])
        TIME = getSimpleTime(result[0])
        SECODE = result[1]
        TOPEN = result[2]
        TCLOSE = result[3]
        HIGH = result[4]
        LOW = result[5]
        VOTRUNOVER = result[6]
        VATRUNOVER = result[7]
        TYClOSE = result[8]
        PCTCHG = (TCLOSE - TYClOSE) / TYClOSE

        valStr = TDATE + ", " + TIME + ", \'"+ SECODE + "\'," \
                + str(TOPEN) + ", " + str(TCLOSE) + ", " + str(HIGH) + ", " + str(LOW) + ", " \
                + str(VATRUNOVER) + ", " + str(VOTRUNOVER) + ", " + str(PCTCHG)  

        insertStr = "insert into "+ table_name + col_str + "values ("+ valStr +")"
        return insertStr 
        
    def getMarketDataTslStr(self, secode, startDate, endDate):
        tsl_str = "code := \'" + secode + "\'; \
        beginDate := " + str(startDate) + "; \
        endDate := " + str(endDate) + "; \
        begt:=inttodate(beginDate); \
        endt:=inttodate(endDate); \
        Setsysparam(PN_Cycle(),cy_1m()); \
        result := select datetimetostr(['date']) as 'date',\
        ['StockID'] as 'secode', ['open'] as 'open',  ['close'] as 'close', \
        ['high']as 'high', ['low']as 'low', ['amount'] as 'VATRUNOVER', ['vol'] as 'VOTRUNOVER',['yclose'] as 'yclose'\
        from markettable datekey  begt to endt + 0.999 of code end;\
        emptyResult := array(); \
        emptyResult[0]:= -1; \
        if result then \
            return result \
        else    \
            return emptyResult "
        return tsl_str

    def getStockData(self, code, startDate, endDate):
        tsl_str = self.getMarketDataTslStr(code, startDate, endDate);
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result        
        
    def getWeightDataTslStr(self, secode, endDate):
        tsl = "secode:=\'" + str(secode) + "\'; \
               endt:=" + str(endDate) +"T; \
               GetBkWeightByDate(secode, endt, result);\
               return result; "
        return tsl
    
    def getWeightData(self, secode, startDate, endDate):
        result = []
        for tmp_enddate in range(startDate, endDate):            
            tsl_str = self.getWeightDataTslStr(secode, tmp_enddate)
            # print tsl_str
            self.curs.execute(tsl_str)
            tmp_result = self.curs.fetchall()
            if len(tmp_result) == 0: 
                continue
            # print tmp_result[0]
            result.append(tmp_result)
        return result

    def getIndexSecode(self):
        secode = ["SH000300", "SZ399903"]
        return secode

    def getStartEndTime(self, oriStartTime, oriEndTime, tableDataStartTime, tableDataEndTime):
        try:
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
        except Exception as e:
            raise(e)

    def getSecodeInfo(self):
        tsl_str = u"name:='A股';StockID:=getbk(name);return StockID;"
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        transResult = []
        for data in result:
            transResult.append(data[0])
        return transResult   