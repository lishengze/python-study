# -*- coding: UTF-8 -*-
import pyodbc
import traceback
import datetime
import threading
import math

from CONFIG import *
from toolFunc import *
from tinysoft import TinySoft
from wind import Wind

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class IndustryNetConnect(TinySoft, Wind):
    def __init__(self,database_type):
        self.data_type = database_type
        TinySoft.__init__(self)
        Wind.__init__(self)

    def __del__(self):
        TinySoft.__del__(self)
        Wind.__del__(self)

    def get_sourceinfo(self, params=[]):
        '''
        根据传入条件，生成获取网络数据的参数。
        针对于行业分类数据, 所需要设置的参数是获取数据的起止时间。
        Args：
            params: 一个list 参数，这里它的第一个数值是 start_date, 第二个是 end_date。
        Returns:
            返回一个以起止时间为上下限的时间序列数组。
        '''
        start_date = params[0]
        end_date = int(params[1])
        tmp_date = start_date
        source_array = []

        while tmp_date <= end_date:
            source_array.append(tmp_date)
            tmp_date = addOneDay(tmp_date)

        return source_array

    def get_cursource(self, table_name, source):
        result = table_name
        return result

    def get_tablename(self, params=[]):
        '''
        获取数据库表名数组
        这里就是起止时间为限的时间数组
        '''
        return self.get_sourceinfo(params)

    def get_netdata_tslstr_b(self, industry_type):
        if industry_type == "申万":        
            indutry_name = u"申万行业"
            primary_industry_name = u"申万一级行业"
            second_industry_name = u"申万二级行业"
        
        if industry_type == "中证":
            indutry_name = u"中证证监会行业"
            primary_industry_name = u"中证一级行业"
            second_industry_name = u"中证二级行业"

        tsl_str = u"indutry_name:=\'" + indutry_name + "\'; \n \
            primary_industry_name := \'" + primary_industry_name + "\'; \n \
            second_industry_name := \'" + second_industry_name + "\'; \n \
            a := GetBkList(indutry_name); \n \
            r:=array(); \n \
            for i:=0 to length(a)-1 do \n  \
            begin \n  \
            primary_industry := a[i]; \n  \
            secondary_industry := getbklist(indutry_name+'\\\\'+ primary_industry);  //得到每个一级行业下的二级行业 \n \
            for j:=0 to length(secondary_industry)-1 do \n \
            begin \n \
                    tmp:=getbk(secondary_industry[j]); \n \
                    tmp:=select thisrow as '代码',primary_industry as primary_industry_name,secondary_industry[j] as second_industry_name from tmp end; \n \
                    r&=tmp;     //相当于r:=r union tmp; \n \
            end; \n \
            end; \n \
            return r; \n "
        
        # print tsl_str
        return tsl_str

    def get_netdata_b(self):        
        result = []
        data_type_array = self.get_sourceinfo()
        secode_array = self.get_allA_secode()
        for i in range(len(secode_array)):
            result.append([])
            result[i].append(secode_array[i][0])
        for data_type in data_type_array:
            tsl_str = self.get_netdata_tslstr(data_type)
            self.curs.execute(tsl_str)
            tmp_rst = self.curs.fetchall()
            for item in tmp_rst:
                secode = item[0]
                for data in result:
                    if data[0] == secode:
                        data.append(item[1])
                        data.append(item[2])
                        break
        return result

    def get_netdata_tslstr(self, date):
        tsl_str = u" StockID:=getbk(\'A股\'); \n \
                    result := array(); \n \
                    date := " + str(date) + "T; \n \
                    setsysparam(pn_date(),date); \n \
                    for i:=0 to length(StockID)-1 do \n \
                    begin \n \
                            code := StockID[i];\n \
                            setsysparam(pn_stock(),code);\n \
                            result[i] := array();\n \
                            result[i][0] := code;\n \
                            result[i][1] := spec(base(10004),code);\n \
                            result[i][2] := spec(base(10032),code);\n \
                            result[i][3] := spec(base(10033),code);\n \
                            result[i][4] := spec(base(10034),code);\n \
                            result[i][5] := StockSWIndustryNameLv1();//  所属申万一级行业名称\n \
                            result[i][6] := StockSWIndustryNameLv2();//  所属申万二级行业名称\n \
                            result[i][7] := StockSWIndustryNameLv3();//  所属申万三级行业名称\n \
                    end;\n \
                    return result;"
        # print tsl_str
        return tsl_str

    def get_netdata(self, conditions=[]):
        '''
        从天软与万得分别获取行业分类的数据并整合到一起。
        '''
        date = conditions
        tsl_str = self.get_netdata_tslstr(date)
        self.curs.execute(tsl_str)
        result  = self.curs.fetchall()
        wind_industry_data = self.get_industry_data(date)
        # if len(result) == 0:
        #     result = None
        trans_rst = []
        for i in range(len(result)):
            trans_rst.append([])
            trans_rst[i].extend(result[i])
            trans_rst[i].insert(0, date)
            for j in range(len(wind_industry_data)):
                if trans_rst[i][1] == wind_industry_data[j][0]:
                    trans_rst[i].extend(wind_industry_data[j][1:])    
            
        return trans_rst        