# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from CONFIG import *
from toolFunc import *
from tinysoft import TinySoft

class MarketTinySoft(TinySoft):
    def __init__(self, datatype):
        self.datatype = datatype
        TinySoft.__init__(self)

    def __del__(self):
        TinySoft.__del__(self)

    def get_sourceinfo(self):
        tsl_str = u"name:='A股';StockID:=getbk(name);return StockID;"
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        transResult = []
        for data in result:
            transResult.append(data[0])
        return transResult   

    def get_netdata_tslstr(self, secode, start_date, end_date):
        tsl_str = "code := \'" + secode + "\'; \
        beginDate := " + str(start_date) + "; \
        endDate := " + str(end_date) + "; \
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

    def get_netdata(self, secode, start_date, end_date):
        tsl_str = self.get_netdata_tslstr(secode, start_date, end_date)
        self.curs.execute(tsl_str)
        result = self.curs.fetchall()
        if len(result) == 1 and result[0][0] == -1:
            result = None
        return result              