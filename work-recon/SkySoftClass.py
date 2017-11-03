# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from databaseClass import MSSQL
from CONFIG import *
from toolFunc import *
from databaseFunc  import *

class SkySoft(object):
    def __init__(self):
        self.__name__ = "SkySoft"
        self.conn = ""
        self.curs = ""

    def startConnect(self, dataSource = "dsn=t1"):
        try:
            self.conn = pyodbc.connect(dataSource)
            self.curs = self.conn.cursor()            
        except Exception as e: 
            raise(e)

    def closeConnect(self):
        try:
            self.curs.close()
            self.conn.close()
        except Exception as e:
            raise e

    def getAllStockDataCostDays(self, oneyearAveTimeSeconds, logFile):
        stockNumb = len(self.getSecodeInfoFromTianRuan())
        print ("stockNumb: %d") % (stockNumb)
        year = 4
        costDays = float(oneyearAveTimeSeconds * year * stockNumb) / 3600.00 / 24.00
        print ("costDays: %f") % (costDays)
        return costDays

    def getInsertStockDataStr(self, result, desTableName):
        try:
            colStr = "(TDATE, TIME, SECODE, TOPEN, TCLOSE, HIGH, LOW, VATRUNOVER, VOTRUNOVER, PCTCHG) "
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

            insertStr = "insert into "+ desTableName + colStr + "values ("+ valStr +")"
            return insertStr
        except Exception as e:
            raise(e)   
        
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
        try:
            dataSource = "dsn=t1"
            tslStr = self.getMarketDataTslStr(code, startDate, endDate);
            self.curs.execute(tslStr)
            result = self.curs.fetchall()
            if len(result) == 1 and result[0][0] == -1:
                result = None
            return result        
        except Exception as e:       
            raise(e)

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