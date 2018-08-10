import datetime
import sys

from CONFIG import *
from func_tool import *
from func_wind import *
from wind import Wind

class ROEDataNet(Wind):
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
        all_a_secode_list = get_a_market_secodelist()
        source = {
            'secode': all_a_secode_list,
            'time': time_list
        }
        return source

   def get_tablename(self, params=[]):
        return self.get_sourceinfo(params)['secode']

    def get_cursource(self, table_name, source):
        result = [table_name]
        result.extend(source['time'])
        return result

    def get_transed_data(self, roe_result, time_result):
        pass
            

    def get_netdata(self, conditions=[]):
        '''
        获取ROE数据
        '''
        secode = conditions[0]
        data_type = conditions[1]
        start_date = conditions[2]
        end_date = conditions[3]

        roe_result = self.wind.wsd(secode,  "qfa_roe", "Days=Alldays,showblank=-1")
        time_result = []

        if roe_result.ErroCode != 0:
            result = self.get_transed_data(roe_result, time_result)
        else:
            raise(Exception("Get_fundament Data Failed, ErroCode is: %s" %(str(tmp.ErrorCode))))

        return result      
        