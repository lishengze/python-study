# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from CONFIG import *
from toolFunc import *
from tinysoft import TinySoft

class WeightTinySoft(TinySoft):
    def __init__(self, datatype):
        self.datatype = datatype
        TinySoft.__init__(self)

    def __del__(self):
        TinySoft.__del__(self)

    def get_sourceinfo(self, params=[]):
        secode = ["SH000300", "SH000016", "SZ399903", \
                  "SH000904", "SH000905", "SH000906", "SH000852"]
        return secode

    def get_netdata_tslstr(self, secode, end_date):
        tsl = "secode:=\'" + str(secode) + "\'; \
               endt:=" + str(end_date) +"T; \
               GetBkWeightByDate(secode, endt, result);\
               emptyResult := array(); \
               emptyResult[0]:= -1; \
               if result then \
                   return result \
               else    \
                   return emptyResult " 

        return tsl

    def get_netdata(self, secode, ori_start_date, ori_end_date):
        result = []
        start_date = ori_start_date
        while start_date <= ori_end_date:
            tsl_str = self.get_netdata_tslstr(secode, start_date)
            start_date = addOneDay(start_date)
            try:
                self.curs.execute(tsl_str)
            except Exception as e:
                error_str = "General error---Execute:"
                if error_str in e[1]:
                    print '\n' + tsl_str + '\n'
                raise(e)       
                     
            tmp_result = self.curs.fetchall()
            if len(tmp_result) == 1 and tmp_result[0][0] == -1:
                continue
            for item in tmp_result:
                result.append(item)
        if len(result) == 0:
            result = None
        return result
