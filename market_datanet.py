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

        # stockidArray = stockidArray[0:10]
        bTest = False
        # bTest = True
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

            # sourceArray = sourceArray[10:11]         

        sourceArray = ["SZ000046"]
        # sourceArray = sourceArray[0:20]

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
        end_time = 0.99
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
        start_datetime = conditions[1]
        end_datetime = conditions[2]
        tsl_str = self.get_netdata_tslstr(secode, start_datetime, end_datetime)
        # print tsl_str
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        # print_data("Origianl Result: ", result)

        transResult = []

        
        if result != None:
            start_date = int(start_datetime)
            end_date = int(end_datetime)
            curdate = start_date
            outstanding_shares_list = {}

            tmp_volume = self.get_Volume(secode, start_date, end_date)
            volume_dict = {}
            for item in tmp_volume:
                date = str(getSimpleDate(item[0]))
                volume_dict[date] = item[1]

            tmp_turnover = self.get_HSL_upgrade(secode, start_date, end_date)
            turnover_dict = {}
            for item in tmp_turnover:
                date = str(item[0])
                turnover_dict[date] = item[1]

            while curdate <= end_date:
                curOutstandingShares = -1
                if str(curdate) in volume_dict and str(curdate) in turnover_dict:
                    curTurnover = turnover_dict[str(curdate)]
                    curVolume = volume_dict[str(curdate)]                                        
                    if curTurnover != 0 and curVolume != -1:
                        curOutstandingShares = curVolume / curTurnover

                outstanding_shares_list[str(curdate)] = curOutstandingShares

                # print curdate, curTurnover, curVolume, curOutstandingShares
                curdate = addOneDay(curdate)

            sumTurnOver = 0
            # print_dict_data("outstanding_shares_list: ", outstanding_shares_list)
            for i in range(len(result)):
                curdate = getSimpleDate(result[i][0])
                cur_turnouver = 0
                if outstanding_shares_list[str(curdate)] != -1:
                    cur_turnouver = result[i][7] / outstanding_shares_list[str(curdate)]
                    sumTurnOver += cur_turnouver
                
                transResult.append(list(result[i]))
                transResult[i].append(cur_turnouver)

            # print "sumTurnOver: ", sumTurnOver

                # result[i].append(cur_turnouver)
                

        return transResult      

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

    def get_secodeList():
        code = "SH000906"
        date = datetime.datetime.now().strftime("%Y%m%d")
        tsl_str = "Return GetBkByDate(\'"+ code + "\',inttodate("+ str(date) + "));"

        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result   

    def get_HSL(self, secode, startdate, enddate):
        tsl_str = "\t\tSetSysParam(PN_Stock(),'"+ str(secode) + "');\n \
                    BegT:=inttodate("+ str(startdate) + "); \n \
                    EndT:=inttodate("+ str(enddate) + "); \n \
                    tmpResult:= StockHsl(BegT,EndT); \n \
                    result := array(); \n \
                    result[0]:= tmpResult; \n \
                    emptyResult := array(); \n \
                    emptyResult[0]:= -1; \n \
                    if result then \n \
                        return result; \n \
                    else    \n \
                        return emptyResult;"
        # print tsl_str

        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        return result[0][0]

    def get_HSL_upgrade(self, secode, startdate, enddate):
        tsl_str = "\t\t\t"
        tsl_str += "Function test_hsl(); \n \
                    Begin \n \
                    SetSysParam(PN_Stock(),\'" + secode + "\'); \n \
                    start_date := " + str(startdate) +  "; \n \
                    end_date := " + str(enddate) + ";\n \
                    cur_date:= start_date; \n \
                    result:= Array();\n \
                    index:=0;\n \
                    while cur_date <= end_date do \n \
                    Begin \n \
                        tmp_start_date := inttodate(cur_date); \n \
                        tmp_end_date := IntToDate(cur_date); \n \
                        tmp_result:= StockHsl(tmp_start_date, tmp_end_date); \n \
                        result[index][0]:=cur_date;\n \
                        result[index][1]:=tmp_result;\n \
                        cur_date := AddOneDay(cur_date);\n \
                        ++index;\n \
                    End;\n \
                    return result; \n \
                    End;\n \
                    Function AddOneDay(cur_date); \n \
                    Begin \n \
                        year := cur_date Div 10000; \n \
                        month := (cur_date - year * 10000) Div 100; \n \
                        day := cur_date - year * 10000 - month * 100  ; \n \
                        day += 1; \n \
                        monthArray := array(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31); \n \
                        if year % 4 = 0 then \n \
                            monthArray[1] := 29; \n \
                        if day > monthArray[month-1] then \n \
                        Begin \n \
                            day := 1; \n \
                            month := month + 1; \n \
                            if month > 12 then \n \
                            Begin \n \
                                month := 1; \n \
                                year := year + 1; \n \
                            End; \n \
                        End; \n \
                        cur_date := year * 10000 + month * 100 + day; \n \
                        return cur_date; \n \
                    End;"
        # print tsl_str

        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        return result
    
    def get_Volume(self, secode, start_date, end_date):
        tsl_str = "code := \'" + secode + "\'; \n \
        beginDate := " + str(int(start_date)) + "; \n \
        endDate := " + str(int(end_date)) + "; \n \
        begt:=inttodate(beginDate); \n \
        endt:=inttodate(endDate); \n \
        Setsysparam(PN_Cycle(), Cy_day()); \n \
        result := select datetimetostr(['date']) as 'date', ['vol'] as 'VOTRUNOVER' \
                  from markettable datekey  begt to endt + 0.99 of code end; \n \
        emptyResult := array(); \n \
        emptyResult[0]:= -1; \n \
        if result then \n \
            return result \n \
        else    \n \
            return emptyResult "

        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        # print result
        return result
