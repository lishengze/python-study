# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from WindPy import *
from CONFIG import *
from toolFunc import *

class Wind(object):
    def __init__(self, log_file, file_lock):
        try:
            self.__name__ = "Wind"
            self.log_file = log_file
            self.file_lock = file_lock
            self.conn = w
            self.startConnect()            
        except:
            exception_str = "[X]: Thread Name " + str(threading.currentThread().getName()) + '\n' \
                          + str(traceback.format_exc())
            self.record_with_rock(exception_str)  
            # raise(Exception(exception_str))  

    def __del__(self):
        self.closeConnect()

    def startConnect(self):
        self.conn.start()
        # print 'wind_start_connect'

    def closeConnect(self):
        self.conn.close()
        # print 'wind_close_connect'

    def record_with_rock(self, info):
        self.file_lock.acquire()
        self.log_file.write(info + "\n")
        print(info)
        self.file_lock.release()

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
        fields = 'open, close, high, low, amt, volume'
        result = self.conn.wsi(code, fields, startDate, endDate, 'Fill=Previous')
        if result.ErrorCode != 0:            
            result = None
        else:
            pass
            # result = result.Data
        return result        
        
    def getStartEndTime(self, oriStartTime, oriEndTime, tableDataStartTime, tableDataEndTime):
        time_array = []
        if tableDataStartTime is None or tableDataEndTime is None:
            time_array.append([oriStartTime, oriEndTime])
        else:
            if oriEndTime > getIntegerDateNow():
                oriEndTime = getIntegerDateNow()

            if tableDataEndTime > getIntegerDateNow():
                tableDataEndTime = getIntegerDateNow()

            if oriStartTime >=  tableDataStartTime and oriEndTime > tableDataEndTime:
                startTime = addOneDay(tableDataEndTime)
                endTime = oriEndTime
                time_array.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime <= tableDataEndTime:
                startTime = oriStartTime
                endTime = minusOneDay(tableDataStartTime)
                time_array.append([startTime, endTime])
            
            if oriStartTime < tableDataStartTime and oriEndTime > tableDataEndTime:
                time_array.append([oriStartTime, minusOneDay(tableDataStartTime)])
                time_array.append([addOneDay(tableDataEndTime), oriEndTime])
        return time_array

    def getSecodeInfo(self):
        all_astock =self.conn.wset("SectorConstituent","sectorId=a001010100000000;field=wind_code");
        if all_astock.ErrorCode != 0:
            raise(Exception('Get Data StockData Failed'))
        else:
            result = []
            for stockid in all_astock.Data[0]:
                stockid_array = stockid.split('.')
                trans_stockid = stockid_array[1] + stockid_array[0]
                result.append(trans_stockid)
            return result