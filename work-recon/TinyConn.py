# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from CONFIG import *
from toolFunc import *

class TinySoft(object):
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
            # raise(Exception(exception_str))  
            # 
        # self.__name__ = "TinySoft"
        # self.conn = ""
        # self.curs = ""
        # self.log_file = log_file
        # self.file_lock = file_lock
        # self.startConnect()
        # raise(Exception('Test Exception in subThread!'))

    def __del__(self):
        self.closeConnect()
        # print '__del__'

    def record_with_rock(self, info):
        self.file_lock.acquire()
        self.log_file.write(info + "\n")
        print(info)
        self.file_lock.release()

    def startConnect(self, dataSource = "dsn=t1"):
        self.conn = pyodbc.connect(dataSource)
        self.curs = self.conn.cursor()   
        # raise(Exception('Test Exception in startConnect!')) 

    def closeConnect(self):
        try:
            self.curs.close()
            self.conn.close()
        except Exception as e:
            raise e

    def getInsertStockDataStr(self, result, desTableName):
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

        insertStr = "insert into "+ desTableName + col_str + "values ("+ valStr +")"
        return insertStr 
        
    def getMarketDataTslStr(self, secode, startDate, endDate):
        try:
            tslStr = "code := \'" + secode + "\'; \
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
            # print tslStr
            return tslStr
        except Exception as e:
            raise(e)   

    def getStockData(self, code, startDate, endDate):
        tslStr = self.getMarketDataTslStr(code, startDate, endDate);
        self.curs.execute(tslStr)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result        
        
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
        try:
            tslStr = u"name:='A股';StockID:=getbk(name);return StockID;"
            self.curs.execute(tslStr)
            result = self.curs.fetchall()
            transResult = []
            for data in result:
                transResult.append(data[0])
            return transResult
        except Exception as e:       
            raise(e)       