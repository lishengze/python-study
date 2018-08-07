# -*- coding: UTF-8 -*-
import datetime
import sys

from CONFIG import *
from func_tool import *
from wind import Wind

reload(sys)
sys.setdefaultencoding('utf-8')

class FundamentalDataNet(Wind):
    def __init__(self,database_type):
        self.data_type = database_type
        Wind.__init__(self)

    def __del__(self):
        Wind.__del__(self)    

    def get_quarterly_windstr(self):
        quarter_paramsstr = "profitnotice_style, profitnotice_date,profitnotice_change,profitnotice_lasteps,\
                            performanceexpress_date,performanceexpress_perfexincome,performanceexpress_perfexprofit,\
                            performanceexpress_perfextotalprofit,performanceexpress_perfexnetprofittoshareholder,performanceexpress_perfexepsdiluted,\
                            performanceexpress_perfexroediluted,performanceexpress_perfextotalassets,performanceexpress_perfexnetassets,\
                            eps_basic,grps,roe_avg,yoyeps_basic,yoy_tr,yoy_or,yoyop,yoyebt,yoyprofit,yoynetprofit,yoynetprofit_deducted,yoy_equity,yoy_assets,\
                            div_cashandstock,div_recorddate,div_exdate,div_paydate,div_prelandate,div_smtgdate,div_impdate"

        quarter_datestr = "unit=1;currencyType=;Period=Q;Days=Alldays;Fill=Previous"
        return (quarter_paramsstr, quarter_datestr)

    def get_daily_windstr(self):
        daily_paramsstr = "ev,pe_ttm,val_pe_deducted_ttm,pb_lf,dividendyield2, gr_ttm, profit_ttm, netprofit_ttm, deductedprofit_ttm"
        daily_datestr = "unit=1;currencyType=;Days=Alldays;Fill=Previous"
        return (daily_paramsstr, daily_datestr)

    def get_sourceinfo(self, params=[]):
        '''
        根据传入条件，生成获取网络数据的参数。
        针对于行业分类数据, 所需要设置的参数是获取数据的起止时间。
        Args：
            params: 一个list 参数，这里它的第一个数值是 start_date, 第二个是 end_date。
        Returns:
            返回一个以起止时间为上下限的时间序列数组。
        '''
        time_array = params
        source = {
            'secode': self.get_allstock_secode(),
            'time': time_array
        }
        return source

    def get_cursource(self, table_name, source):
        tmpdata = table_name.split('_')
        secode = tmpdata[0][2:] + '.' + tmpdata[0][0:2]
        datatype = tmpdata[1] + '_' + tmpdata[2]
        time_array = source['time']
        result = []
        result.append(secode)
        result.append(datatype)
        result.extend(time_array)
        return result

    def get_tablename(self, params=[]):
        '''
        获取数据库表名数组
        以证券代码为基础，加上日度后缀和季度后缀；
        每只证券对应两个数据表一个存储每日都更新的数据，一个存储季度更新的数据。
        '''
        stockid_array = self.get_allstock_secode()
        tablename_array = []
        for i in range(len(stockid_array)):
            ori_table_name = stockid_array[i][7:9] + stockid_array[i][0:6]   
            dailydata_tablename = ori_table_name + '_daily_data'
            quarterlydata_tablename = ori_table_name + '_quarterly_data'
            tablename_array.append(dailydata_tablename)
            tablename_array.append(quarterlydata_tablename)
        return tablename_array

    def get_netdata(self, conditions=[]):
        '''
        从天软与万得分别获取行业分类的数据并整合到一起。
        '''
        secode = conditions[0]
        data_type = conditions[1]
        start_date = conditions[2]
        end_date = conditions[3]
        
        if data_type == 'daily_data':
            params_str, date_str = self.get_daily_windstr()
        elif data_type == 'quarterly_data':
            params_str, date_str = self.get_quarterly_windstr()
        else:
            raise(Exception("Unknown data type"))  

        result = self.wind.wsd(secode, params_str, start_date, end_date, date_str)
        oridata = result.Data
        transdata = []
        date_count = length(oridata[0])
        item_count = length(oridata)
        for i in range(date_count):
            transdata.append([])
            for j in range(item_count):
                transdata[i].append(oridata[j][i])
        return transdata      
        