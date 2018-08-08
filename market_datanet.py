# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math
import random

from CONFIG import *
from func_tool import *
from func_secode import *
from func_time import *
from tinysoft import TinySoft

from market_database import MarketDatabase
# from wind import Wind

class MarketTinySoft(TinySoft):
    def __init__(self, datatype):
        self.datatype = datatype
        tmpData = datatype.split('_')
        self.timeType = tmpData[1]
        TinySoft.__init__(self)

    def __del__(self):
        TinySoft.__del__(self)

    def get_sourceinfo(self, params=[]):
        print (params)
        time_array = params[0:2]
        code_type = 'stock'
        if len(params) > 2:
            code_type = params[2]

        stockidArray = self.get_a_market_secodelist()
        # file_name = 'D:/excel/2018成长分红.xlsx'
        # stockidArray = get_execl_code(file_name)   

        indexidArray = self.get_Index_secode()
        sourceArray = []

        bTest = False
        # bTest = True
        if bTest:
            # # print "self.datatype: ", self.datatype
            # database_obj = MarketDatabase(host="localhost", db=self.datatype)
            # table_name = database_obj.getDatabaseTableInfo()
            # # print "table_name: ", table_name

            # if len(table_name) == 0:                    
            #     test_numb = 12
            #     # sourceArray = random.sample(stockidArray, test_numb)
            #     sourceArray = stockidArray[0:test_numb]
            # else:
            #     sourceArray = table_name           
            file_name = 'D:/excel/2018成长分红.xlsx'
            sourceArray = get_execl_code(file_name)    
        else:       
            print ("code_type: %s" % (code_type))     
            if 'index' in code_type:
                for indexCode in indexidArray:
                    sourceArray.append(indexCode)

            if 'stock' in code_type:
                for secode in stockidArray:
                    sourceArray.append(getCompleteSecode(secode,"tinysoft"))   

        # sourceArray = ["SH601330"]
        # sourceArray = sourceArray[15:23]
        # sourceArray = ["SH600000"]
        # sourceArray = ["SH600051"]
        # sourceArray = ["SH600145"]
        # sourceArray = ["SZ000415"]
        # sourceArray = ["SH000300"]
        # sourceArray = sourceArray[0:100]
        
        # sourceArray = ["SH000300",'SH000908', 'SH000909', 'SH000910', \
        #                 'SH000911', 'SH000912', 'SH000913','SH000914', 
        #                 'SH000915', 'SH000917', \
        #                 "SZ000001", "SZ000002", "SZ000063", "SH600009", \
        #                 "SH600011", "SH600019", "SH600028", "SH600104", \
        #                 "SH600276", "SH600519", "SH600588"]

        # sourceArray = ['SH600588']

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
        return self.get_sourceinfo(params)['secode']

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
        return tsl_str

    def get_preclose_data(self, secode, startdate, enddate):
        tsl_str = self.get_preclose_tslstr(secode, enddate)
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()    
        return result    

    def get_Volume(self, secode, start_date, end_date):
        end_time = 0.99
        start_time = start_date - int(start_date)
        tsl_str = "code := \'" + secode + "\'; \n \
        beginDate := " + str(int(start_date)) + "; \n \
        endDate := " + str(int(end_date)) + "; \n \
        begt:=inttodate(beginDate); \n \
        endt:=inttodate(endDate); \n \
        Setsysparam(PN_Cycle(), Cy_day()); \n \
        result := select datetimetostr(['date']) as 'date', ['vol'] as 'VOTRUNOVER' \
                  from markettable datekey  begt + " + str(start_time) + " to endt + 0.99 of code end; \n \
        emptyResult := array(); \n \
        emptyResult[0]:= -1; \n \
        if result then \n \
            return result \n \
        else    \n \
            return emptyResult "

        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result

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

    def trans_ori_netdata(self, oridata):
        TDATE = int(getSimpleDate(oridata[0]))
        TIME = int(getSimpleTime(oridata[0]))
        SECODE = oridata[1]
        TOPEN = oridata[2]
        TCLOSE = oridata[3]
        HIGH = oridata[4]
        LOW = oridata[5]
        VATRUNOVER = oridata[7]
        VOTRUNOVER = oridata[6]
        YClOSE = oridata[8]
        if YClOSE != 0:
            PCTCHG = (TCLOSE - YClOSE) / YClOSE
        else:
            PCTCHG = 100000000
        result = []
        result.append(TDATE)
        result.append(TIME)
        result.append(SECODE)
        result.append(TOPEN)
        result.append(TCLOSE)
        result.append(HIGH)
        result.append(LOW)
        result.append(VATRUNOVER)
        result.append(VOTRUNOVER)
        result.append(PCTCHG)
        result.append(YClOSE)
        return result

    def complete_rate_data(self, oridata):
        open_price  = oridata[3]
        close_price = oridata[4]
        high_price  = oridata[5]
        low_price   = oridata[6]
        open_rate   = open_price / close_price
        high_rate   = high_price / close_price
        low_rate    = low_price / close_price   
        oridata.append(open_rate)   
        oridata.append(high_rate)   
        oridata.append(low_rate)
        return oridata     

    def trans_wind_result(self, ori_result, code):
        for item in ori_result:
            item.insert(1, code)
            item[8] = item[3]*(1-item[8])
        return ori_result

    def get_netdata(self, conditions=[]):
        result = []
        secode = conditions[0]
        start_datetime = conditions[1]
        end_datetime = conditions[2]

        is_get_wind_data = False
        if is_get_wind_data == True and (secode == "SH000951" or secode == "SH000952" or secode == "SH000849"):
            windObj = Wind()
            code = trans_tinycode_to_wind(secode) 
            startdate = transto_wind_datetime(start_datetime)
            enddate = transto_wind_datetime(end_datetime)
            print("code: %s, startdate: %s, enddate: %s" %(code, startdate, enddate))
            keyvalue_list = ["open", "close", "high", "low", "volume", "amt", "pct_chg"]
            result = windObj.get_histdata(code, keyvalue_list, startdate, enddate, self.timeType)
            result = self.trans_wind_result(result, code)

            keyvalue_list = ["volume"]
            volume_result = windObj.get_histdata(code, keyvalue_list, startdate, enddate)
        else:
            tsl_str = self.get_netdata_tslstr(secode, start_datetime, end_datetime)
            try:
                self.curs.execute(tsl_str)
            except Exception as e:
                pyodbc_error = "S1000"
                exception_info = traceback.format_exc()
                if pyodbc_error in exception_info:
                    print ('当前选择时间没有交易日')
                    return []
                else:
                    raise e
        
            result = self.curs.fetchall()
            if len(result) == 1 and result[0][0] == -1:
                result = None

            volume_result = self.get_Volume(secode, start_datetime, end_datetime)

        complete_result = []        
        if result != None and volume_result != None:
            start_date = int(start_datetime)
            end_date = int(end_datetime)

            curdate = start_date
            outstanding_shares_list = {}

            volume_dict = {}
            for item in volume_result:
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
                curdate = addOneDay(curdate)

            sumTurnOver = 0
            # print_dict_data("outstanding_shares_list: ", outstanding_shares_list)
            for cur_data in result:                
                trans_result = self.trans_ori_netdata(cur_data)
                curdate = str(trans_result[0])
                cur_turnouver = 0
                if outstanding_shares_list[curdate] != -1:
                    cur_turnouver = trans_result[7] / outstanding_shares_list[curdate]
                    sumTurnOver += cur_turnouver
                trans_result.append(cur_turnouver)
                trans_result = self.complete_rate_data(trans_result)
                # print (trans_result)
                complete_result.append(trans_result)

        return complete_result      

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
        print (tsl_str)
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

    def get_secodeList(self):
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
    

