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

    def get_transed_data(self, unit_result, key_list):
        result = []
        for i in range(len(unit_result.Times)):
            result.append([])

        for i in range(len(unit_result.Times)):
            result[i].append(str(unit_result.Times[i]).replace('-', ''))
            result[i].append('150000')
            for j in range(len(key_list)):
                result[i].append(unit_result.Data[j][i])
            result[i][6] = 1 / result[i][6]
        
        return result
            

    def get_netdata(self, conditions=[]):
        '''
        从天软与万得分别获取行业分类的数据并整合到一起。
        '''
        secode = conditions[0]
        data_type = conditions[1]
        start_date = conditions[2]
        end_date = conditions[3]
        key_list = ["estpeg_FTM", "pe_ttm", "pb_lf", "ps_ttm","pcf_ocf_ttm","eps_ttm","ev",]
        unit_result = self.wind.wsd(secode,  ",".join(key_list), start_date, end_date, "unit=1")

        if unit_result.ErrorCode != 0 
            result = self.get_transed_data(unit_result, key_list)
        else:
            raise(Exception("Get_fundament Data Failed, ErroCode is: %s" %(str(tmp.ErrorCode))))

        return result      
        