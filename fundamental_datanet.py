import datetime
import sys

from CONFIG import *
from func_tool import *
from func_wind import *
from wind import Wind

class FundamentalDataNet(Wind):
    def __init__(self,database_type):
        self.data_type = database_type
        Wind.__init__(self)

    def __del__(self):
        Wind.__del__(self)    

    def get_sourceinfo(self, params=[]):
        '''
        根据传入条件，生成获取网络数据的参数。
        针对于基本面数据, 所需要设置的参数是获取数据的起止时间。
        Args：
            params: 一个list 参数，这里它的第一个数值是 start_date, 第二个是 end_date。
        Returns:
            返回一个dict {
                'secode':
                'time':
            }
        '''
        time_list = params
        source = {
            'secode': get_a_market_secodelist(),
            'time': time_list
        }
        return source

   def get_tablename(self, params=[]):
        return self.get_sourceinfo(params)['secode']

    def get_cursource(self, table_name, source):
        result = [table_name]
        result.extend(source['time'])
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

    def get_transed_data(self, col_result, ps_result, pb_result):
        pass

    def get_netdata(self, conditions=[]):
        '''
        从天软与万得分别获取行业分类的数据并整合到一起。
        '''
        secode = conditions[0]
        data_type = conditions[1]
        start_date = conditions[2]
        end_date = conditions[3]

        col_result = self.wind.wsd(secode, "pe, cfps, eps_ttm, mv_ref, roe,", start_date, end_date, \
                                    "currencyType=;unit=1;ruleType=10")
        ps_result = self.wind.wsd(secode, "ps", start_date, end_date, "ruleType=2")
        pb_result = self.wind.wsd(secode, "pb", start_date, end_date, "ruleType=3")
        # w.wsd("600000.SH", "estpeg_FTM,pe_ttm,pb_lf,ps_ttm,pcf_ocf_ttm,qfa_roe,eps_ttm,ev", "2017-07-05", "2018-08-08", "unit=1")
        result = self.get_transed_data(col_result, ps_result, pb_result)

        oridata = result.Data
        transdata = []
        date_count = length(oridata[0])
        item_count = length(oridata)
        for i in range(date_count):
            transdata.append([])
            for j in range(item_count):
                transdata[i].append(oridata[j][i])
        return transdata      
        