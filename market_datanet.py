# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math
import random

from CONFIG import *
from toolFunc import *
from tinysoft import TinySoft

from market_database import MarketDatabase


class MarketTinySoft(TinySoft):
    def __init__(self, datatype):
        self.datatype = datatype
        tmpData = datatype.split('_')
        self.timeType = tmpData[1]
        TinySoft.__init__(self)

    def __del__(self):
        TinySoft.__del__(self)

    def get_sourceinfo(self, params=[]):
        time_array = params
        stockidArray = self.get_allA_secode()
        indexidArray = self.get_Index_secode()
        sourceArray = []

        bTest = True
        if bTest:
            # print "self.datatype: ", self.datatype
            database_obj = MarketDatabase(host="localhost", db=self.datatype)
            table_name = database_obj.getDatabaseTableInfo()
            # print "table_name: ", table_name

            if len(table_name) == 0:                    
                test_numb = 12
                # sourceArray = random.sample(stockidArray, test_numb)
                sourceArray = stockidArray[0:test_numb]
            else:
                sourceArray = table_name               
        else:
            for indexCode in indexidArray:
                sourceArray.append(indexCode)

            for secode in stockidArray:
                sourceArray.append(secode)            

        source = {
            'secode': sourceArray,
            'time': time_array
        }
        return source

    def get_index_source_info(self, params=[]):
        time_array = params
        stockidArray = self.get_allA_secode()
        indexidArray = self.get_Index_secode()
        sourceArray = []
        for indexCode in indexidArray:
            sourceArray.append(indexCode)

        source = {
            'secode': sourceArray,
            'time': time_array
        }
        return source        

    def get_tablename(self, params=[]):
        return self.get_sourceinfo()['secode']

    def get_cursource(self, table_name, source):
        result = [table_name]
        result.extend(source['time'])
        return result

    def get_timetypeTslstr(self):
        timeTypeStr = "Cy_" + self.timeType + "()"
        return timeTypeStr 

    def get_preclose_tslstr(self, secode, date):
        tsl_str = "SetSysParam(PN_Stock(), \'"+ secode + " \'); \
                   EndT:=inttodate("+ str(date) + "); \
                   return StockPrevClose4(EndT);"

    def get_preclose_data(self, secode, startdate, enddate):
        tsl_str = self.get_preclose_tslstr(secode, enddate)
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()        

    def get_netdata_tslstr(self, secode, start_date, end_date):
        end_time = end_date - int(end_date)
        start_time = start_date - int(start_date)
        timeTypeStr = self.get_timetypeTslstr()
        tsl_str = "code := \'" + secode + "\'; \n \
        beginDate := " + str(int(start_date)) + "; \n \
        endDate := " + str(int(end_date)) + "; \n \
        begt:=inttodate(beginDate); \n \
        endt:=inttodate(endDate); \n \
        Setsysparam(PN_Cycle()," + timeTypeStr + "); \n \
        result := select datetimetostr(['date']) as 'date',\n \
        ['StockID'] as 'secode', ['open'] as 'open',  ['close'] as 'close', \n \
        ['high']as 'high', ['low']as 'low', ['amount'] as 'VATRUNOVER', ['vol'] as 'VOTRUNOVER',['yclose'] as 'yclose'\n \
        from markettable datekey  begt + " + str(start_time) + " to endt + "+ str(end_time) +" of code end; \n \
        emptyResult := array(); \n \
        emptyResult[0]:= -1; \n \
        if result then \n \
            return result \n \
        else    \n \
            return emptyResult "
        # print tsl_str
        return tsl_str

    def get_netdata(self, conditions=[]):
        result = []
        secode = conditions[0]
        start_date = conditions[1]
        end_date = conditions[2]
        tsl_str = self.get_netdata_tslstr(secode, start_date, end_date)
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result      

    def get_dailydata_str(self, secode, start_date, end_date):
        timeTypeStr = self.get_timetypeTslstr()
        tsl_str = "code := \'" + secode + "\'; \n \
        beginDate := " + str(int(start_date)) + "; \n \
        endDate := " + str(int(end_date)) + "; \n \
        begt:=inttodate(beginDate); \n \
        endt:=inttodate(endDate); \n \
        Setsysparam(PN_Cycle(),"+ timeTypeStr + "); \n \
        result := select datetimetostr(['date']) as 'date',\n \
        ['StockID'] as 'secode', ['open'] as 'open',  ['close'] as 'close', \n \
        ['high']as 'high', ['low']as 'low', ['amount'] as 'VATRUNOVER', ['vol'] as 'VOTRUNOVER',['yclose'] as 'yclose'\n \
        from markettable datekey  begt to endt of code end; \n \
        emptyResult := array(); \n \
        emptyResult[0]:= -1; \n \
        if result then \n \
            return result \n \
        else    \n \
            return emptyResult "
        print tsl_str
        return tsl_str

    def get_dailydata(self, conditions=[]):
        result = []
        secode = conditions[0]
        start_date = conditions[1]
        end_date = conditions[2]
        
        tsl_str = self.get_dailydata_str(secode, start_date, end_date)
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result    