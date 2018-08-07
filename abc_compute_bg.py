from market_database import MarketDatabase
from func_connect import *
from func_tool import *
from func_strategy import *

from excel import EXCEL
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


import threading

class ABCCompute(object):
    '''
    计算ABC 策略    

    '''
    def __init__(self, dbhost, trade_type, data_type, high_price_days, \
                data_start_date, data_end_date, \
                secode_list, fall_value_list, \
                rebound_rise_value_list, rebound_fall_value_list,\
                k1_list=[], k2_list=[], k3_list=[]):
        '''     
        @dbhost: 数据源选项           
        @secode_list: 证券代码列表
        @fall_value_list: 单日下降幅度遍历区间
        @rebound_rise_value_list: 反弹上升幅度-与Pmin比较 -- 遍历区间;
        @rebound_fall_value_list: 反弹下降幅度-与Pmax比较 -- 遍历区间;
        @buy_sale_price_type_list: 计算进出场的价格选择方式列表;
        '''
        self.dbhost = dbhost
        self.trade_type = trade_type
        self.data_type = data_type
        self.data_start_date = data_start_date
        self.data_end_date = data_end_date
        
        self.secode_list = secode_list
        self.fall_value_list = fall_value_list
        self.rebound_rise_value_list = rebound_rise_value_list
        self.rebound_fall_value_list = rebound_fall_value_list
        self.k1_list = k1_list
        self.k2_list = k2_list
        self.k3_list = k3_list
        self.excel_obj = EXCEL()
        self.figure_count = 0
        self.high_price_days = high_price_days
        self.trade_cost = -0.002

        self.init_lock()
        self.init_dir()
        self.init_database()
        self.init_result_datastructure()
                        
    def init_lock(self):
        self.lock = threading.Lock()

    def init_result_datastructure(self):
        self.index_code = 'SH000300'
        self.thread_list = []
        self.complete_count = 0
        self.sum_result = [[],[],[],[],[],[],[]] # 第一存储年化收益，最大净值， 第二个存储所有净值， 第三个存储所有回撤
        if len(self.k1_list) == 0:
            self.sum_compute_count = len(self.fall_value_list) * len(self.rebound_rise_value_list) \
                                    * len(self.rebound_fall_value_list) 
        else:
            self.sum_compute_count = len(self.fall_value_list) * len(self.k1_list) * len(self.k2_list) * len(self.k3_list) 
        print('self.sum_compute_count: %d, self.high_price_days: %d ' \
                %(self.sum_compute_count, self.high_price_days))

        self.date_data = self.database_obj.get_date_data(self.data_start_date, self.data_end_date)
        self.secode_hist_data = self.get_secode_histdata_dict()       
        self.secode_highprice_dict = self.get_high_price()  

    def init_dir(self):
        user_dir = '\ABC_Result\\%d\\%s\\New_High_Days_%d\\' %(len(self.secode_list), self.trade_type, self.high_price_days)  
        self.dir_name = os.getcwd() + user_dir
        if not os.path.exists(self.dir_name):
            os.makedirs(self.dir_name)
    
    def init_database(self):
        self.database_obj = get_database_obj(self.data_type, host = self.dbhost)

    def log_info(self, info_str, exception_flag = False):
        print (info_str)
        # self.log_file.write(info_str + '\n'+'\n')
        pass

    def set_log_file(self, file_name):
        self.log_write_lock = threading.Lock()
        dir_name = os.getcwd() + '\ABC_Result\\%d\\' %(len(self.secode_list))
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name)
            except Exception as e:
                exception_info = str(traceback.format_exc())
                dir_exit_error = '文件已存在'
                if dir_exit_error not in exception_info:
                    raise(e)            
        self.log_file = open(file_name, 'w+')            

    def get_secode_histdata_dict(self):
        result = {}
        column_str = ' TDATE, TOPEN, TCLOSE, HIGH, LOW, PCTCHG, VATRUNOVER '
        for secode in self.secode_list:
            result[secode] = self.database_obj.get_histdata_by_date(startdate=self.data_start_date, enddate=self.data_end_date, \
                                                                    table_name=secode, cloumn_str=column_str)
        return result

    def get_secode_startindex_dict(self, date_numb):
        result = {}
        for secode in self.secode_hist_data:
            result[secode] = date_numb - len(self.secode_hist_data[secode])
        return result

    def get_high_price(self):
        result = {}
        for secode in self.secode_list:
            result[secode] = self.get_high_price_atom(self.secode_hist_data[secode])
        return result
                
    def get_high_price_atom(self, ori_data):
        result = []
        index = 0
        max_value = ori_data[0][2]
        while index < len(ori_data):
            if index < self.high_price_days:
                if max_value <= ori_data[index][2]:
                    max_value = ori_data[index][2]
                result.append(max_value)
            else:
                if self.is_achieve_new_high(ori_data[index-self.high_price_days+1:index+1]):
                    max_value = ori_data[index][2]
                result.append(max_value)
            index += 1
        return result

    def is_achieve_new_high(self, ori_data):
        result = True
        new_data = ori_data[len(ori_data)-1][2]
        for data in ori_data:
            if data[2] > new_data:
                result = False
                break
        return result

    def get_test_data(self):
        # secode_list = ['SH600000', 'SH600004']
        # self.date_data = [[0], [1], [2], [3], [4], [5], [6], [7]]                
        # self.secode_hist_data = {
        #     'SH600000': [[1, 11,  10,      15, 9, 0.1], 
        #                 [2,  10,  9.2,     12, 7, -0.08],  # 加入观察集
        #                 [3,  9,   9.568,   11, 5, 0.04],   # 创新低, 并且反弹
        #                 [4,  9.5, 10.0464, 14, 10, 0.05],  # 日内最高价 >= Pmin*(1+4%) 加入投资集合，收益 (10.0464 - 9.5) / 9.5 == 0.0575: 当日收盘价比开盘价
        #                 [5,  10,  10.2473, 16, 13.8, 0.02],  # 继续持有， 收益 0.02 : 当日涨跌幅
        #                 [6,  9.8, 10.0423, 13, 10, -0.02],  # 日内最低价 <= Pmax*(1-2%) 卖出，收益 (9.8 - 10.2473) / 10.2473 == -0.04365: 当日开盘价比上日收盘价
        #                 [7,  11, 11.0423, 13, 11, 0]  # 日内最低价 <= Pmax*(1-2%) 卖出，收益 (9.8 - 10.2473) / 10.2473 == -0.04365: 当日开盘价比上日收盘价                                                 
        #     ],
        #     'SH600004': [[0, 11,  10,      15, 9, 0.1], 
        #                 [1,  10,  9.2,     12, 7, -0.08],  # 加入观察集
        #                 [2,  9,   9.568,   11, 5, 0.04],   # 创新低, 并且反弹
        #                 [3,  9.5, 10.0464, 14, 10, 0.05],  # 日内最高价 >= Pmin*(1+4%) 加入投资集合，收益 (10.0464 - 9.5) / 9.5 == 0.0575: 当日收盘价比开盘价
        #                 [4,  10,  10.2473, 16, 13.8, 0.02],  # 继续持有， 收益 0.02 : 当日涨跌幅
        #                 [5,  9.8, 10.0423, 13, 10, -0.02],  # 日内最低价 <= Pmax*(1-2%) 卖出，收益 (9.8 - 10.2473) / 10.2473 == -0.04365: 当日开盘价比上日收盘价
        #                 [6,  11, 11.0423, 13, 11, 0],  # 日内最低价 <= Pmax*(1-2%) 卖出，收益 (9.8 - 10.2473) / 10.2473 == -0.04365: 当日开盘价比上日收盘价       
        #                 [7,  10, 10.1589, 12, 9, -0.08]         # 再次进入观察集                                 
        #     ]            
        # }

        secode_list = ['SH600000']
        self.date_data = [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12]]                
        self.secode_hist_data = {
            'SH600000': [[1, 11,      10,      15,      9,       0.1,   100], 
                        [2,  10,      9.2,     12,      7,      -0.08,  100], # 加入观察集
                        [3,  9.2,     9.2,     9.2,     9.2,     0,     0],   # 停牌
                        [4,  9,       9.568,   11,      5,       0.04,  100], # 创新低, 并且反弹
                        [5,  9.5,     10.0464, 14,      10,      0.05,  100], # 日内最高价 >= Pmin*(1+4%) 加入买入集合;
                        [6,  10.0464, 10.0464, 10.0464, 10.0464, 0,     0],   # 停牌;
                        [7,  13.8,    10.2473, 11,      10,      0.02,  100], # 当日购买，并判断是否需要卖出，收益 (10.2473 - 10)/10 == 0.002437: 当日收盘价比开盘价;
                        [8,  9.8,     10.0423, 13,      10,     -0.02,  100], # 日内最低价 <= Pmax*(1-2%) 下一日卖出，移入卖出集合, 收益: -0.02
                        [9,  10.0423, 10.0423, 10.0423, 10.0423, 0,     0],   # 停牌;
                        [10, 10.0423, 10.0423, 10.0423, 10.0423, 0,     0],   # 停牌;
                        [11, 10.0423, 10.0423, 10.0423, 10.0423, 0,     0],   # 停牌;
                        [12, 11,      11.0423, 13,      11,      0,     100]  # 卖出: 收益 (11 - 10.0423) / 10.0423 == 0.09536: 当日开盘价比上日收盘价;                                     
            ]         
        }
        return secode_list, self.date_data, self.secode_hist_data

    def compute_daily_result_highlow(self, fall_value, rebound_rise_value, rebound_fall_value):
        date_numb = len(self.date_data)
        secode_startindex_dict = self.get_secode_startindex_dict(date_numb)

        unobserve_list = deep_copy_list(self.secode_list) 
        observe_dict = {}
        hold_dict = {}        
        buy_dict = {}
        sale_list = []
        result = []

        start_index = 0
        buy_earning_list = []
        hold_earning_list = []    
        sale_earning_list = []
        all_earning_list = []
        date_list = []
        while start_index < date_numb:
            cur_sum_earning = 0
            cur_sale_earning = 0
            cur_buy_earning = 0
            cur_hold_earning = 0
            cur_buyhold_earning = 0

            # 遍历卖出集合, 判断是否跌停或者停牌；
            # 1. 否: 卖不出去，继续持有在卖出与持仓组合中 
            # 2. 是: 判断开盘价是否创新高：
            #      1) 是，不卖了， 卖了不划算,记录最新高价;
            #      2) 否, 卖了， 计算卖出收益，并将当前卖出的证券从持仓与卖出组合中删除
            curr_saled_list = []
            curr_rehold_list = []
            for secode in sale_list:
                cur_index         = start_index - secode_startindex_dict[secode]
                amount            = self.secode_hist_data[secode][cur_index][6]
                today_chg         = self.secode_hist_data[secode][cur_index][5]
                today_open        = self.secode_hist_data[secode][cur_index][1]
                yesterday_close   = self.secode_hist_data[secode][cur_index-1][2]
                if amount != 0 and today_chg > -0.09:                                        
                    if today_open > yesterday_close \
                    and today_open > float(hold_dict[secode]) * (1 + rebound_fall_value): 
                        curr_rehold_list.append(secode)
                    else:
                        cur_sale_earning += (today_open - yesterday_close) / yesterday_close
                        unobserve_list.append(secode)
                        curr_saled_list.append(secode) 
            if len(curr_saled_list) != 0:
                cur_sale_earning /= len(curr_saled_list)
                remove_list_item(sale_list, curr_saled_list)
                pop_dict_item(hold_dict, curr_saled_list)
            remove_list_item(sale_list, curr_rehold_list)

            # 遍历持仓集合, 是否停牌
            # 1. 停牌: 停止此次操作;
            # 2. 不停牌: 
            #   1) 计算收益 更新最高价
            #   2) 判断是否卖出： 卖-加入卖出组合
            for secode in hold_dict:
                cur_index  = start_index - secode_startindex_dict[secode]     
                amount     = self.secode_hist_data[secode][cur_index][6]
                if amount != 0:              
                    today_high = self.secode_hist_data[secode][cur_index][3]
                    today_low  = self.secode_hist_data[secode][cur_index][4]
                    today_chg  = self.secode_hist_data[secode][cur_index][5]
                    cur_hold_earning += today_chg
                    if today_high > hold_dict[secode]:
                        hold_dict[secode] = today_high 
                    if today_low < float(hold_dict[secode]) * (1 + rebound_fall_value):
                        if secode not in sale_list:
                            sale_list.append(secode)                         
                
            # 遍历买入集合, 
            # 1. 更新最高价
            # 2. 是否停牌或涨停
            #   1) 是，当天无法购买，继续放在买入集，等待下一个交易日
            #   2) 否，再判断当日的开盘价是否满足止损条件 
            #       1) 否, 说明当日未出现骤降, 可以购买，计算买入收益，
            #              将其加入持仓组合并同时记录当前最高价，并将其从买入集合中删除;
            #       2) 是, 说明又开始骤降，将其再次放入观察集合中; 
            curr_buy_list = []
            curr_abandon_list = []
            curr_stay_list = []
            for secode in buy_dict:
                cur_index    = start_index - secode_startindex_dict[secode]
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_chg    = self.secode_hist_data[secode][cur_index][5]
                today_high   = self.secode_hist_data[secode][cur_index][3]
                today_open   = self.secode_hist_data[secode][cur_index][1]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                yesterday_close = self.secode_hist_data[secode][cur_index-1][2]
                if amount != 0 and today_chg < 0.09:            
                    if today_open < float(buy_dict[secode]) * (1 + rebound_fall_value) \
                    or today_open < yesterday_close:
                        curr_abandon_list.append(secode)
                    else:
                        cur_buy_earning += (today_close - today_open) / today_open   
                        curr_buy_list.append(secode)  
                        if today_high > buy_dict[secode]:
                            buy_dict[secode] = today_high                        
                        hold_dict[secode] = buy_dict[secode] 
                else:
                    curr_stay_list.append(secode)
                    if today_close > buy_dict[secode]:
                        buy_dict[secode] = today_close                        
            pop_dict_item(buy_dict, curr_abandon_list)
            pop_dict_item(buy_dict, curr_buy_list)     
            pop_dict_item(observe_dict, curr_buy_list)
            pop_dict_item(observe_dict, curr_stay_list)
            if len(hold_dict) != 0:
                cur_buyhold_earning = (cur_buy_earning + cur_hold_earning) / len(hold_dict)
                                    
            # 遍历观察集合,
            # 1. 是否停牌：否 -> 是否创新低
            #   1) 创新低： 更新新低;
            #   2) 未创新低: 判断是否满足反弹涨幅
            #       a. 满足反弹涨幅: 将其加入买入集合，并记录当前最低价格，从观察集合中删除
            prebuy_list = []
            for secode in observe_dict:
                cur_index    = start_index - secode_startindex_dict[secode]
                amount       = self.secode_hist_data[secode][cur_index][6]
                if amount != 0:
                    today_high   = self.secode_hist_data[secode][cur_index][3]
                    today_low    = self.secode_hist_data[secode][cur_index][4]
                    today_chg    = self.secode_hist_data[secode][cur_index][5]
                    if today_low < observe_dict[secode]:
                        observe_dict[secode] = today_low
                    if today_high > float(observe_dict[secode]) * (1 + rebound_rise_value) \
                    and today_chg > 0:
                        prebuy_list.append(secode)
                        buy_dict[secode] = today_high
            # pop_dict_item(observe_dict, prebuy_list)      

            # 遍历参考集合, 将符合下降幅度的证券添加到观察集合中         
            for secode in unobserve_list:
                cur_index = start_index - secode_startindex_dict[secode]
                if cur_index < 0: continue
                amount = self.secode_hist_data[secode][cur_index][6]
                if amount != 0:   
                    today_low = self.secode_hist_data[secode][cur_index][4]
                    today_chg = self.secode_hist_data[secode][cur_index][5]
                    if today_chg < fall_value:
                        unobserve_list.remove(secode)
                        observe_dict[secode] = today_low
        
            cur_sum_earning = float(1 + cur_buyhold_earning) * float(1 + cur_sale_earning)
            buy_earning_list.append(float(1 + cur_buy_earning))
            hold_earning_list.append(float(1 + cur_hold_earning))
            sale_earning_list.append(float(1 + cur_sale_earning))
            all_earning_list.append(float(cur_sum_earning))
            date_list.append(self.date_data[start_index][0])

            info_str = 'Date: %s, unobserve_list: %s, observe_dict: %s, buy_dict: %s,  curr_buy_list: %s, sale_list: %s, curr_saled_list: %s, hold_dict: %s, cur_sum_earning: %s' % \
                        (str(self.date_data[start_index][0]), str(unobserve_list), str(observe_dict), str(buy_dict), str(curr_buy_list), \
                        str(sale_list), str(curr_saled_list), str(hold_dict), str(cur_sum_earning))

            self.log_info(info_str)
            start_index += 1
        result.append(buy_earning_list)
        result.append(hold_earning_list)
        result.append(sale_earning_list)
        result.append(all_earning_list)
        result.append(date_list)

        return result

    def compute_daily_result_close_nextday(self, fall_value, rebound_rise_value, rebound_fall_value):
        date_numb = len(self.date_data)
        secode_startindex_dict = self.get_secode_startindex_dict(date_numb)

        unobserve_list =  deep_copy_list(self.secode_list) 
        secode_position_dict = self.get_secode_position(self.secode_list)
        observe_dict = {}
        hold_dict = {}        
        buy_dict = {}
        sale_list = []
        result = []

        start_index = 0
        buy_earning_list = []
        hold_earning_list = []    
        sale_earning_list = []
        all_earning_list = []
        date_list = []
        secode_set_matrix =[]
        secode_set_matrix.append(self.get_set_matrix_title(self.secode_list))

        while start_index < date_numb:
            cur_sum_earning = 0
            cur_sale_earning = 0
            cur_buy_earning = 0
            cur_hold_earning = 0
            cur_buyhold_earning = 0
            curr_set_list = self.get_init_set_list(len(self.secode_list))

            # 遍历卖出集合, 判断是否跌停或者停牌；
            # 1. 是: 卖不出去，继续持有在卖出与持仓组合中 
            # 2. 否: 判断 当日开盘 > 昨日收盘  and  当日开盘 > 止损价格，
            #        说明当日趋势可能是上涨不卖， 从卖出集合删除，保留在持仓集合中以后再进行判断：
            curr_saled_list = []
            curr_rehold_list = []
            for secode in sale_list:
                cur_index         = start_index - secode_startindex_dict[secode]
                amount            = self.secode_hist_data[secode][cur_index][6]
                today_chg         = self.secode_hist_data[secode][cur_index][5]
                today_open        = self.secode_hist_data[secode][cur_index][1]
                yesterday_close   = self.secode_hist_data[secode][cur_index-1][2]
                curr_set_list[secode_position_dict[secode]] = '准备卖出'
                try:
                    if amount != 0 and today_chg > -0.09:                                        
                        if today_open <= hold_dict[secode]:  
                        # if today_open < yesterday_close \
                        # and today_open < float(hold_dict[secode]) * (1 + rebound_fall_value): 
                            cur_sale_earning += (today_open - yesterday_close) / yesterday_close
                            unobserve_list.append(secode)
                            curr_saled_list.append(secode)      
                            curr_set_list[secode_position_dict[secode]] = '卖出进入待观察集合'                   
                        else:
                            curr_set_list[secode_position_dict[secode]] = '卖不出去 继续持仓'     
                            curr_rehold_list.append(secode)                           
                except KeyError as e:
                    print(hold_dict)
                    print(sale_list)
                    raise e

            if len(curr_saled_list) != 0:
                cur_sale_earning /= len(curr_saled_list)
                remove_list_item(sale_list, curr_saled_list)
                pop_dict_item(hold_dict, curr_saled_list)
            remove_list_item(sale_list, curr_rehold_list)

            # 遍历持仓集合, 是否停牌
            # 1. 停牌: 停止此次操作;
            # 2. 不停牌: 
            #   1) 计算收益 更新最高价
            #   2) 判断是否卖出： 卖-加入卖出组合
            for secode in hold_dict:
                cur_index  = start_index - secode_startindex_dict[secode]     
                amount     = self.secode_hist_data[secode][cur_index][6]
                curr_set_list[secode_position_dict[secode]] = '持仓'   
                if amount != 0:              
                    # today_high   = self.secode_hist_data[secode][cur_index][3]
                    # today_low    = self.secode_hist_data[secode][cur_index][4]
                    today_chg    = self.secode_hist_data[secode][cur_index][5]
                    today_close  = self.secode_hist_data[secode][cur_index][2]  
                    cur_hold_earning += today_chg
                    if today_close > hold_dict[secode]:
                        hold_dict[secode] = today_close
                    if today_close < float(hold_dict[secode]) * (1 + rebound_fall_value):
                        if secode not in sale_list:
                            sale_list.append(secode)           
                    curr_set_list[secode_position_dict[secode]] = '持仓'             
            curr_hold_numb = len(hold_dict)
            # 遍历买入集合, 
            # 1. 更新最高价
            # 2. 是否停牌或涨停
            #   1) 是，当天无法购买，继续放在买入集，等待下一个交易日
            #   2) 否，再判断当日的开盘价是否满足止损条件 and 开盘价 > 昨日收盘价
            #       1) 否, 说明当日未出现下降趋势, 可以购买，计算买入收益，
            #              将其加入持仓组合并同时记录当前最高价，并将其从买入集合中删除;
            #       2) 是, 说明可能开始下降了，将其再次放入观察集合中; 
            curr_buy_list = []
            curr_abandon_list = []
            curr_stay_list = []
            for secode in buy_dict:
                cur_index    = start_index - secode_startindex_dict[secode]
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_chg    = self.secode_hist_data[secode][cur_index][5]
                # today_high   = self.secode_hist_data[secode][cur_index][3]
                today_open   = self.secode_hist_data[secode][cur_index][1]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                yesterday_close = self.secode_hist_data[secode][cur_index-1][2]
                curr_set_list[secode_position_dict[secode]] = '准备买入'
                if amount != 0 and today_chg < 0.09:            
                    # if today_open >= float(buy_dict[secode]) * (1 + rebound_fall_value) \
                    # and today_open >= yesterday_close:
                    cur_buy_earning += (today_close - today_open) / today_open   
                    curr_buy_list.append(secode)  
                    if today_close > buy_dict[secode]:
                        buy_dict[secode] = today_close                        
                    hold_dict[secode] = buy_dict[secode] 
                    curr_set_list[secode_position_dict[secode]] = '买入 进入持仓'
                    # else:
                    #     curr_abandon_list.append(secode)       
                    #     if secode not in observe_dict and secode not in unobserve_list:
                    #         unobserve_list.append(secode)                
                else:
                    curr_set_list[secode_position_dict[secode]] = '无法买入'
                    curr_stay_list.append(secode)
                    if today_close > buy_dict[secode]:
                        buy_dict[secode] = today_close                        
            pop_dict_item(buy_dict, curr_abandon_list)
            pop_dict_item(buy_dict, curr_buy_list)     

            pop_dict_item(observe_dict, curr_buy_list)
            pop_dict_item(observe_dict, curr_stay_list)

            if len(hold_dict) != 0:
                cur_buyhold_earning = (cur_buy_earning + cur_hold_earning) / len(hold_dict)
            if len(curr_buy_list) != 0:
                cur_buy_earning /= len(curr_buy_list)
            if curr_hold_numb != 0:
                cur_hold_earning /= curr_hold_numb

            # 遍历观察集合,
            # 1. 是否停牌：否 -> 是否创新低
            #   1) 创新低： 更新新低;
            #   2) 未创新低: 判断是否满足反弹涨幅
            #       a. 满足反弹涨幅: 将其加入买入集合，并记录当前最低价格，从观察集合中删除
            prebuy_list = []
            for secode in observe_dict:
                cur_index    = start_index - secode_startindex_dict[secode]
                amount       = self.secode_hist_data[secode][cur_index][6]
                curr_set_list[secode_position_dict[secode]] = '观察'
                if amount != 0:
                    # today_high   = self.secode_hist_data[secode][cur_index][3]
                    # today_low    = self.secode_hist_data[secode][cur_index][4]
                    today_chg    = self.secode_hist_data[secode][cur_index][5]
                    today_close  = self.secode_hist_data[secode][cur_index][2]  
                    if today_close < observe_dict[secode]:
                        observe_dict[secode] = today_close
                    if today_close > float(observe_dict[secode]) * (1 + rebound_rise_value) \
                    and today_chg > 0:
                        prebuy_list.append(secode)
                        buy_dict[secode] = today_close
                        curr_set_list[secode_position_dict[secode]] = '准备买入'
            # pop_dict_item(observe_dict, prebuy_list)      

            # 遍历参考集合, 将符合下降幅度的证券添加到观察集合中      
            # if self.date_data[start_index][0] == 20110117:
            #     print (unobserve_list)

            curr_observe_list = []
            for secode in unobserve_list:
                cur_index = start_index - secode_startindex_dict[secode]
                # if self.date_data[start_index][0] == 20110117:
                #     print ('secode: %s, cur_index: %d' %(secode, cur_index))
                if cur_index < 0: continue
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]
                # if self.date_data[start_index][0] == 20110117:
                #     print('secode: %s, amout: %f, today_chg: %f' % (secode, amount, today_chg))
                if amount != 0:   
                    # today_low = self.secode_hist_data[secode][cur_index][4]
                    today_chg = self.secode_hist_data[secode][cur_index][5]
                    if today_chg < fall_value:
                        curr_observe_list.append(secode)
                        observe_dict[secode] = today_close
                        if '卖出' in curr_set_list[secode_position_dict[secode]]:
                            curr_set_list[secode_position_dict[secode]] = '卖出 并进入观察'
                        else:
                            curr_set_list[secode_position_dict[secode]] = '进入观察'
            remove_list_item(unobserve_list, curr_observe_list)
        
            cur_sum_earning = float(1 + cur_buyhold_earning) * float(1 + cur_sale_earning)

            buy_earning_list.append(float(cur_buy_earning))
            hold_earning_list.append(float(cur_hold_earning))
            sale_earning_list.append(float(cur_sale_earning))
            all_earning_list.append(float(cur_sum_earning-1))
            date_list.append(self.date_data[start_index][0])

            curr_set_list.insert(0, self.date_data[start_index][0])
            secode_set_matrix.append(curr_set_list)

            info_str = 'Date: %s, unobserve_list: %s, observe_dict: %s, buy_dict: %s,  curr_buy_list: %s, sale_list: %s, curr_saled_list: %s, hold_dict: %s, cur_sum_earning: %s' % \
                        (str(self.date_data[start_index][0]), str(unobserve_list), str(observe_dict), str(buy_dict), str(curr_buy_list), \
                        str(sale_list), str(curr_saled_list), str(hold_dict), str(cur_sum_earning))

            # self.log_info(info_str)
            start_index += 1
        result.append(date_list)
        result.append(buy_earning_list)
        result.append(hold_earning_list)
        result.append(sale_earning_list)
        result.append(all_earning_list)
        result.append(secode_set_matrix)
        return result        

    def compute_daily_result_close_todaytrade_simple(self, fall_value, rebound_rise_value, rebound_fall_value):
        date_numb = len(self.date_data)
        secode_startindex_dict = self.get_secode_startindex_dict(date_numb)
        secode_position_dict = self.get_secode_position(self.secode_list)
        unobserve_list =  deep_copy_list(self.secode_list) 
        observe_dict = {}
        hold_dict = {}

        start_index = 0
        date_list = []
        earning_list = []
        secode_earning_matrix = []
        secode_set_matrix =[]

        secode_earning_matrix.append(self.get_earning_matrix_title(self.secode_list))
        secode_set_matrix.append(self.get_set_matrix_title(self.secode_list))

        hold_timecount = 0
        while start_index < date_numb:
            curr_earning = 0
            curr_set_list = self.get_init_set_list(len(self.secode_list))
            curr_earning_list = self.get_init_earning_list(len(self.secode_list))

            curr_saled_list = []
            
            for secode in hold_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                curr_set_list[secode_position_dict[secode]] = '持仓'             
                hold_timecount += 1 
                if amount != 0:                    
                    curr_earning += today_chg
                    curr_earning_list[secode_position_dict[secode]] = today_chg                    
                    if today_close > hold_dict[secode]:
                        hold_dict[secode] = today_close
                    elif today_close < float(hold_dict[secode]) * (1 + rebound_fall_value):
                        curr_saled_list.append(secode)
                        unobserve_list.append(secode)
                        curr_set_list[secode_position_dict[secode]] = '当日卖出'
                        
            if len(hold_dict) != 0:
                curr_earning /= len(hold_dict)
            pop_dict_item(hold_dict, curr_saled_list)

            curr_buy_list = []
            for secode in observe_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                curr_set_list[secode_position_dict[secode]] = '观察'

                if amount != 0:
                    if observe_dict[secode] > today_close:
                        observe_dict[secode] = today_close
                    elif today_close > float(observe_dict[secode]) * (1 + rebound_rise_value):
                        hold_dict[secode] = today_close
                        curr_buy_list.append(secode)
                        curr_set_list[secode_position_dict[secode]] = '当日买入进入持仓'
            pop_dict_item(observe_dict, curr_buy_list)

            curr_delete_unobserve_list = []
            for secode in unobserve_list:
                cur_index = start_index - secode_startindex_dict[secode]
                
                if '当日卖出' in curr_set_list[secode_position_dict[secode]]:
                    curr_set_list[secode_position_dict[secode]] = '当日卖出进入待观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '待观察'

                if cur_index < 0: continue

                amount = self.secode_hist_data[secode][cur_index][6]                
                if amount != 0:                    
                    today_chg   = self.secode_hist_data[secode][cur_index][5] 
                    today_close = self.secode_hist_data[secode][cur_index][2] 
                    if today_chg < fall_value:
                        curr_delete_unobserve_list.append(secode)
                        observe_dict[secode] = today_close
                        if '当日卖出' in curr_set_list[secode_position_dict[secode]]:
                            curr_set_list[secode_position_dict[secode]] = '当日卖出进入观察'
                        else:
                            curr_set_list[secode_position_dict[secode]] = '观察'
            remove_list_item(unobserve_list, curr_delete_unobserve_list)

            date_list.append(self.date_data[start_index][0])
            earning_list.append(float(curr_earning))
            curr_earning_list.append(curr_earning)
            curr_earning_list.insert(0, self.date_data[start_index][0])
            curr_set_list.insert(0, self.date_data[start_index][0])

            #记录每支股票的收益，集合属性:
            secode_earning_matrix.append(curr_earning_list)
            secode_set_matrix.append(curr_set_list)

            start_index += 1

        result = []
        result.append(date_list)
        result.append(earning_list)
        result.append(secode_earning_matrix)
        result.append(secode_set_matrix)
        print('hold_timecount: %d ' % ( hold_timecount))
        return result

    def compute_daily_result_close_todaytrade(self, fall_value, rebound_rise_value, rebound_fall_value):
        date_numb = len(self.date_data)
        secode_startindex_dict = self.get_secode_startindex_dict(date_numb)
        secode_position_dict = self.get_secode_position(self.secode_list)

        unobserve_list =  deep_copy_list(self.secode_list) 
        observe_dict = {}
        wait_buy_dict = {}
        hold_dict = {}
        wait_sale_dict = {}
        
        start_index = 0
        date_list = []
        earning_list = []
        secode_earning_matrix = []
        secode_set_matrix =[]
        secode_close_matrix = []
        secode_chg_matrix = []

        secode_earning_matrix.append(self.get_earning_matrix_title(self.secode_list))
        secode_set_matrix.append(self.get_set_matrix_title(self.secode_list))
        secode_close_matrix.append(self.get_close_matrix_title(self.secode_list))
        secode_chg_matrix.append(self.get_change_matrix_title(self.secode_list))

        # rise_fall_count = 0
        rise_stop_count = 0
        fall_stop_count = 0
        hold_timecount = 0

        while start_index < date_numb:
            curr_earning = 0
            curr_set_list = self.get_init_set_list(len(self.secode_list))
            curr_earning_list = self.get_init_earning_list(len(self.secode_list))
            curr_close_list = get_value_list(len(self.secode_list), 0)
            curr_change_list = get_value_list(len(self.secode_list), 0)

            curr_add_hold_dict = {}
            curr_add_wait_sale_dict = {}
            curr_add_wait_buy_dict = {}
            curr_add_observe_dict = {}
            curr_add_unobserve_dict = {}

            curr_delete_hold_list = []
            curr_delete_wait_sale_list = []
            curr_delete_wait_buy_list = []            
            curr_delete_observe_list = []
            curr_delete_unobserve_list = []

            curr_buy_count = 0

            for secode in unobserve_list:
                cur_index = start_index - secode_startindex_dict[secode]
                if cur_index < 0: 
                    curr_set_list[secode_position_dict[secode]] = '待观察'
                    continue
   
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5] 
                curr_set_list[secode_position_dict[secode]] = '待观察'
                curr_close_list[secode_position_dict[secode]] = today_close
                curr_change_list[secode_position_dict[secode]] = today_chg

                if amount != 0:                    
                    if today_chg < fall_value:
                        curr_delete_unobserve_list.append(secode)
                        curr_add_observe_dict[secode] = today_close
                        curr_set_list[secode_position_dict[secode]] = '观察'
                    else:
                        curr_set_list[secode_position_dict[secode]] = '待观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '待观察'

            for secode in observe_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                curr_set_list[secode_position_dict[secode]] = '观察'
                curr_close_list[secode_position_dict[secode]] = today_close
                curr_change_list[secode_position_dict[secode]] = today_chg
                
                if amount != 0:                                        
                    if observe_dict[secode] > today_close:
                        observe_dict[secode] = today_close

                    if today_close > float(observe_dict[secode]) * (1 + rebound_rise_value):
                        maximum_price = today_close
                        minimum_price = observe_dict[secode]
                        curr_delete_observe_list.append(secode)
                        if today_chg >= 0.09:
                            rise_stop_count += 1
                            curr_set_list[secode_position_dict[secode]] = '当日涨停，继续等待次日买入'
                            curr_add_wait_buy_dict[secode] = [maximum_price, minimum_price]
                        else:
                            curr_buy_count += 1
                            curr_earning += self.trade_cost
                            curr_earning_list[secode_position_dict[secode]] = self.trade_cost                             
                            curr_set_list[secode_position_dict[secode]] = '直接买入，放入持仓'
                            curr_add_hold_dict[secode] = maximum_price
                    else:
                        curr_set_list[secode_position_dict[secode]] = '观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '观察'

            for secode in wait_buy_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                curr_set_list[secode_position_dict[secode]] = '等待买入'         
                curr_close_list[secode_position_dict[secode]] = today_close      
                curr_change_list[secode_position_dict[secode]] = today_chg

                if amount != 0:                                    
                    if today_close > wait_buy_dict[secode][0]:
                        wait_buy_dict[secode][0] = today_close                    
                    if today_close < wait_buy_dict[secode][1]:
                        wait_buy_dict[secode][1] = today_close     

                    if today_chg >= 0.09:       
                        rise_stop_count += 1
                        curr_set_list[secode_position_dict[secode]] = '再次涨停,继续等待买入'     
                    else:
                        curr_delete_wait_buy_list.append(secode)
                        maximum_price = wait_buy_dict[secode][0]
                        minimum_price = wait_buy_dict[secode][1]   

                        if today_close < float(maximum_price) * (1 + rebound_fall_value):
                            curr_add_observe_dict[secode] = minimum_price  
                            curr_set_list[secode_position_dict[secode]] = '跌破止损, 放入观察集'
                        else:
                            curr_add_hold_dict[secode] = maximum_price
                            curr_buy_count += 1
                            curr_earning += self.trade_cost
                            curr_earning_list[secode_position_dict[secode]] = self.trade_cost                             
                            curr_set_list[secode_position_dict[secode]] = '买入，放入持仓'    
                else:
                    curr_set_list[secode_position_dict[secode]] = '等待买入'    

            for secode in hold_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                curr_set_list[secode_position_dict[secode]] = '持仓' 
                curr_close_list[secode_position_dict[secode]] = today_close   
                curr_change_list[secode_position_dict[secode]] = today_chg     

                hold_timecount += 1     
                if amount != 0:                    
                    curr_earning += float(today_chg)
                    curr_earning_list[secode_position_dict[secode]] = today_chg                    
                    if today_close > hold_dict[secode]:
                        hold_dict[secode] = today_close
                    elif today_close < float(hold_dict[secode]) * (1 + rebound_fall_value):
                        maximum_price = hold_dict[secode]
                        minimum_price = today_close
                        curr_delete_hold_list.append(secode)
                        if today_chg <= -0.09:
                            fall_stop_count += 1
                            curr_add_wait_sale_dict[secode] = [maximum_price, minimum_price]                            
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,但跌停,等待次日卖出'
                        elif today_chg <= fall_value:
                            curr_add_observe_dict[secode] = minimum_price
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,放入观察集合'
                        else:
                            curr_add_unobserve_dict[secode] = hold_dict[secode]
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,放入待观察集合'
                else:
                    curr_set_list[secode_position_dict[secode]] = '持仓'      

            for secode in wait_sale_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                curr_set_list[secode_position_dict[secode]] = '等待卖出'   
                curr_close_list[secode_position_dict[secode]] = today_close   
                curr_change_list[secode_position_dict[secode]] = today_chg

                hold_timecount += 1      
                if amount != 0:                         
                    curr_earning += float(today_chg)
                    curr_earning_list[secode_position_dict[secode]] = today_chg  

                    if today_close > wait_sale_dict[secode][0]:
                        wait_sale_dict[secode][0] = today_close                    
                    if today_close < wait_sale_dict[secode][1]:
                        wait_sale_dict[secode][1] = today_close

                    if today_chg <= -0.09:
                        curr_set_list[secode_position_dict[secode]] = '当日跌停，继续等待次日卖出'
                        fall_stop_count += 1
                    else:
                        curr_delete_wait_sale_list.append(secode)
                        maximum_price = wait_sale_dict[secode][0]
                        minimum_price = wait_sale_dict[secode][1]
                        if today_close >= float(maximum_price) * (1 + rebound_fall_value):
                            curr_add_hold_dict[secode] = maximum_price                       
                            curr_set_list[secode_position_dict[secode]] = '卖出当日涨回止损，放入持仓'
                        else:
                            curr_add_observe_dict[secode] = minimum_price
                            curr_set_list[secode_position_dict[secode]] = '卖出，放入观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '等待卖出'                                          

            if len(hold_dict) + len(wait_sale_dict) + curr_buy_count != 0:
                curr_earning /= (len(hold_dict) + len(wait_sale_dict) + curr_buy_count)

            remove_list_item(unobserve_list, curr_delete_unobserve_list)
            remove_dict_item(observe_dict, curr_delete_observe_list)
            remove_dict_item(wait_buy_dict, curr_delete_wait_buy_list)
            remove_dict_item(hold_dict, curr_delete_hold_list)
            remove_dict_item(wait_sale_dict, curr_delete_wait_sale_list)

            add_list_item(unobserve_list, curr_add_unobserve_dict)
            add_dict_item(observe_dict, curr_add_observe_dict)
            add_dict_item(wait_buy_dict, curr_add_wait_buy_dict)
            add_dict_item(hold_dict, curr_add_hold_dict)
            add_dict_item(wait_sale_dict, curr_add_wait_sale_dict)

            date_list.append(self.date_data[start_index][0])
            earning_list.append(float(curr_earning))
            curr_earning_list.append(curr_earning)
            curr_earning_list.insert(0, self.date_data[start_index][0])
            curr_set_list.insert(0, self.date_data[start_index][0])
            curr_close_list.insert(0, self.date_data[start_index][0])
            curr_change_list.insert(0, self.date_data[start_index][0])

            #记录每支股票的收益，集合属性:
            secode_earning_matrix.append(curr_earning_list)
            secode_set_matrix.append(curr_set_list)
            secode_close_matrix.append(curr_close_list)
            secode_chg_matrix.append(curr_change_list)

            start_index += 1

        result = []
        result.append(date_list)
        result.append(earning_list)
        result.append(secode_earning_matrix)
        result.append(secode_set_matrix)
        result.append(secode_close_matrix)
        result.append(secode_chg_matrix)
        result.append((rise_stop_count + fall_stop_count) / hold_timecount)

        print('rise_stop_count: %d, fall_stop_count: %d, sum: %d, hold_timecount: %d '\
             % (rise_stop_count, fall_stop_count, rise_stop_count + fall_stop_count, hold_timecount))
        return result

    def compute_daily_result_close_todaytrade_improve(self, fall_value, rebound_rise_value, rebound_fall_value):
        date_numb = len(self.date_data)
        secode_startindex_dict = self.get_secode_startindex_dict(date_numb)
        secode_position_dict = self.get_secode_position(self.secode_list)

        unobserve_list =  deep_copy_list(self.secode_list) 
        observe_dict = {}
        wait_buy_dict = {}
        hold_dict = {}
        wait_sale_dict = {}
        
        start_index = 0
        date_list = []
        earning_list = []
        secode_earning_matrix = []
        secode_set_matrix =[]
        secode_high_price_matrix = []
        secode_close_matrix = []
        secode_chg_matrix = []

        secode_earning_matrix.append(self.get_earning_matrix_title(self.secode_list))
        secode_set_matrix.append(self.get_set_matrix_title(self.secode_list))
        secode_close_matrix.append(self.get_close_matrix_title(self.secode_list))
        secode_chg_matrix.append(self.get_change_matrix_title(self.secode_list))
        secode_high_price_matrix.append(self.get_high_price_matrix_title(self.secode_list))

        # rise_fall_count = 0
        rise_stop_count = 0
        fall_stop_count = 0
        hold_timecount = 0

        while start_index < date_numb:
            curr_earning = 0
            curr_set_list = self.get_init_set_list(len(self.secode_list))
            curr_earning_list = self.get_init_earning_list(len(self.secode_list))
            curr_close_list = get_value_list(len(self.secode_list), 0)
            curr_change_list = get_value_list(len(self.secode_list), 0)
            curr_high_price_list = get_value_list(len(self.secode_list), 0)

            curr_add_hold_dict = {}
            curr_add_wait_sale_dict = {}
            curr_add_wait_buy_dict = {}
            curr_add_observe_dict = {}
            curr_add_unobserve_dict = {}

            curr_delete_hold_list = []
            curr_delete_wait_sale_list = []
            curr_delete_wait_buy_list = []            
            curr_delete_observe_list = []
            curr_delete_unobserve_list = []
            curr_buy_count = 0

            for secode in unobserve_list:
                cur_index = start_index - secode_startindex_dict[secode]
                if cur_index < 0:
                    curr_set_list[secode_position_dict[secode]] = '待观察'
                    continue
   
                amount          = self.secode_hist_data[secode][cur_index][6]
                today_close     = self.secode_hist_data[secode][cur_index][2]  
                today_chg       = self.secode_hist_data[secode][cur_index][5]
                high_price      = self.secode_highprice_dict[secode][cur_index]
                curr_fall_value = (today_close - high_price) / high_price

                curr_set_list[secode_position_dict[secode]] = '待观察'
                curr_close_list[secode_position_dict[secode]] = today_close
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price

                if amount != 0:                    
                    if curr_fall_value < fall_value:
                        curr_delete_unobserve_list.append(secode)
                        curr_add_observe_dict[secode] = today_close
                        curr_set_list[secode_position_dict[secode]] = '观察'
                    else:
                        curr_set_list[secode_position_dict[secode]] = '待观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '待观察'

            for secode in observe_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                high_price   = self.secode_highprice_dict[secode][cur_index]

                curr_set_list[secode_position_dict[secode]] = '观察'
                curr_close_list[secode_position_dict[secode]] = today_close
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price
                
                if amount != 0:                                        
                    if observe_dict[secode] > today_close:
                        observe_dict[secode] = today_close

                    if today_close > float(observe_dict[secode]) * (1 + rebound_rise_value):
                        maximum_price = today_close
                        minimum_price = observe_dict[secode]
                        curr_delete_observe_list.append(secode)
                        if today_chg >= 0.09:
                            rise_stop_count += 1
                            curr_set_list[secode_position_dict[secode]] = '当日涨停，继续等待次日买入'
                            curr_add_wait_buy_dict[secode] = [maximum_price, minimum_price]
                        else:
                            curr_buy_count += 1
                            curr_earning += self.trade_cost
                            curr_earning_list[secode_position_dict[secode]] = self.trade_cost                                
                            curr_set_list[secode_position_dict[secode]] = '直接买入，放入持仓'
                            curr_add_hold_dict[secode] = maximum_price
                    else:
                        curr_set_list[secode_position_dict[secode]] = '观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '观察'

            for secode in wait_buy_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                high_price   = self.secode_highprice_dict[secode][cur_index]
                curr_set_list[secode_position_dict[secode]] = '等待买入'         
                curr_close_list[secode_position_dict[secode]] = today_close      
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price

                if amount != 0:                                    
                    if today_close > wait_buy_dict[secode][0]:
                        wait_buy_dict[secode][0] = today_close                    
                    if today_close < wait_buy_dict[secode][1]:
                        wait_buy_dict[secode][1] = today_close     

                    if today_chg >= 0.09:       
                        rise_stop_count += 1
                        curr_set_list[secode_position_dict[secode]] = '再次涨停,继续等待买入'     
                    else:
                        curr_delete_wait_buy_list.append(secode)
                        maximum_price = wait_buy_dict[secode][0]
                        minimum_price = wait_buy_dict[secode][1]   

                        if today_close < float(maximum_price) * (1 + rebound_fall_value):
                            curr_add_observe_dict[secode] = minimum_price  
                            curr_set_list[secode_position_dict[secode]] = '跌破止损, 放入观察集'
                        else:
                            curr_add_hold_dict[secode] = maximum_price
                            curr_buy_count += 1
                            curr_earning += self.trade_cost
                            curr_earning_list[secode_position_dict[secode]] = self.trade_cost     
                            curr_set_list[secode_position_dict[secode]] = '买入，放入持仓'    
                else:
                    curr_set_list[secode_position_dict[secode]] = '等待买入'    

            for secode in hold_dict:
                cur_index       = start_index - secode_startindex_dict[secode]     
                amount          = self.secode_hist_data[secode][cur_index][6]
                today_close     = self.secode_hist_data[secode][cur_index][2]  
                today_chg       = self.secode_hist_data[secode][cur_index][5]   
                high_price      = self.secode_highprice_dict[secode][cur_index]
                curr_fall_value = (today_close - high_price) / high_price

                curr_set_list[secode_position_dict[secode]] = '持仓' 
                curr_close_list[secode_position_dict[secode]] = today_close   
                curr_change_list[secode_position_dict[secode]] = today_chg     
                curr_high_price_list[secode_position_dict[secode]] = high_price

                hold_timecount += 1     
                if amount != 0:                    
                    curr_earning += float(today_chg)
                    curr_earning_list[secode_position_dict[secode]] = today_chg                    
                    if today_close > hold_dict[secode]:
                        hold_dict[secode] = today_close
                    elif today_close < float(hold_dict[secode]) * (1 + rebound_fall_value):
                        maximum_price = hold_dict[secode]
                        minimum_price = today_close
                        curr_delete_hold_list.append(secode)
                        if today_chg <= -0.09:
                            fall_stop_count += 1
                            curr_add_wait_sale_dict[secode] = [maximum_price, minimum_price]                            
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,但跌停,等待次日卖出'
                        elif curr_fall_value <= fall_value:
                            curr_add_observe_dict[secode] = minimum_price
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,放入观察集合'
                        else:
                            curr_add_unobserve_dict[secode] = hold_dict[secode]
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,放入待观察集合'
                else:
                    curr_set_list[secode_position_dict[secode]] = '持仓'      

            for secode in wait_sale_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]  
                high_price   = self.secode_highprice_dict[secode][cur_index] 
                curr_set_list[secode_position_dict[secode]] = '等待卖出'   
                curr_close_list[secode_position_dict[secode]] = today_close   
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price

                hold_timecount += 1      
                if amount != 0:                         
                    curr_earning += float(today_chg)
                    curr_earning_list[secode_position_dict[secode]] = today_chg

                    if today_close > wait_sale_dict[secode][0]:
                        wait_sale_dict[secode][0] = today_close                    
                    if today_close < wait_sale_dict[secode][1]:
                        wait_sale_dict[secode][1] = today_close

                    if today_chg <= -0.09:
                        curr_set_list[secode_position_dict[secode]] = '当日跌停，继续等待次日卖出'
                        fall_stop_count += 1
                    else:
                        curr_delete_wait_sale_list.append(secode)
                        maximum_price = wait_sale_dict[secode][0]
                        minimum_price = wait_sale_dict[secode][1]
                        if today_close >= float(maximum_price) * (1 + rebound_fall_value):
                            curr_add_hold_dict[secode] = maximum_price                       
                            curr_set_list[secode_position_dict[secode]] = '卖出当日涨回止损，放入持仓'
                        else:
                            curr_add_observe_dict[secode] = minimum_price
                            curr_set_list[secode_position_dict[secode]] = '卖出，放入观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '等待卖出'                                          

            if len(hold_dict) + len(wait_sale_dict) + curr_buy_count != 0:
                curr_earning /= (len(hold_dict) + len(wait_sale_dict) + curr_buy_count)

            remove_list_item(unobserve_list, curr_delete_unobserve_list)
            remove_dict_item(observe_dict, curr_delete_observe_list)
            remove_dict_item(wait_buy_dict, curr_delete_wait_buy_list)
            remove_dict_item(hold_dict, curr_delete_hold_list)
            remove_dict_item(wait_sale_dict, curr_delete_wait_sale_list)

            add_list_item(unobserve_list, curr_add_unobserve_dict)
            add_dict_item(observe_dict, curr_add_observe_dict)
            add_dict_item(wait_buy_dict, curr_add_wait_buy_dict)
            add_dict_item(hold_dict, curr_add_hold_dict)
            add_dict_item(wait_sale_dict, curr_add_wait_sale_dict)

            date_list.append(self.date_data[start_index][0])
            earning_list.append(float(curr_earning))
            curr_earning_list.append(curr_earning)
            curr_earning_list.insert(0, self.date_data[start_index][0])
            curr_set_list.insert(0, self.date_data[start_index][0])
            curr_close_list.insert(0, self.date_data[start_index][0])
            curr_change_list.insert(0, self.date_data[start_index][0])
            curr_high_price_list.insert(0, self.date_data[start_index][0])

            #记录每支股票的收益，集合属性:
            secode_earning_matrix.append(curr_earning_list)
            secode_set_matrix.append(curr_set_list)
            secode_close_matrix.append(curr_close_list)
            secode_chg_matrix.append(curr_change_list)
            secode_high_price_matrix.append(curr_high_price_list)

            start_index += 1

        result = []
        result.append(date_list)
        result.append(earning_list)
        result.append(secode_earning_matrix)
        result.append(secode_set_matrix)
        result.append(secode_close_matrix)
        result.append(secode_chg_matrix)
        result.append(secode_high_price_matrix)
        # result.append((rise_stop_count + fall_stop_count)/hold_timecount)

        # print('rise_stop_count: %d, fall_stop_count: %d, sum: %d, hold_timecount: %d '\
        #      % (rise_stop_count, fall_stop_count, rise_stop_count + fall_stop_count, hold_timecount))
        return result

    def compute_todaytrade_improve_B(self, fall_value, k1, k2, k3):
        date_numb = len(self.date_data)
        secode_startindex_dict = self.get_secode_startindex_dict(date_numb)
        secode_position_dict = self.get_secode_position(self.secode_list)

        unobserve_list =  deep_copy_list(self.secode_list) 
        observe_dict = {}
        wait_buy_dict = {}
        hold_dict = {}
        wait_sale_dict = {}
        
        start_index = 0
        date_list = []
        earning_list = []
        secode_earning_matrix = []
        secode_set_matrix =[]
        secode_high_price_matrix = []
        secode_close_matrix = []
        secode_chg_matrix = []

        secode_earning_matrix.append(self.get_earning_matrix_title(self.secode_list))
        secode_set_matrix.append(self.get_set_matrix_title(self.secode_list))
        secode_close_matrix.append(self.get_close_matrix_title(self.secode_list))
        secode_chg_matrix.append(self.get_change_matrix_title(self.secode_list))
        secode_high_price_matrix.append(self.get_high_price_matrix_title(self.secode_list))

        # rise_fall_count = 0
        rise_stop_count = 0
        fall_stop_count = 0
        hold_timecount = 0

        while start_index < date_numb:
            curr_earning = 0
            curr_set_list = self.get_init_set_list(len(self.secode_list))
            curr_earning_list = self.get_init_earning_list(len(self.secode_list))
            curr_close_list = get_value_list(len(self.secode_list), 0)
            curr_change_list = get_value_list(len(self.secode_list), 0)
            curr_high_price_list = get_value_list(len(self.secode_list), 0)

            curr_add_hold_dict = {}
            curr_add_wait_sale_dict = {}
            curr_add_wait_buy_dict = {}
            curr_add_observe_dict = {}
            curr_add_unobserve_dict = {}

            curr_delete_hold_list = []
            curr_delete_wait_sale_list = []
            curr_delete_wait_buy_list = []            
            curr_delete_observe_list = []
            curr_delete_unobserve_list = []
            curr_buy_count = 0

            for secode in unobserve_list:
                cur_index = start_index - secode_startindex_dict[secode]
                if cur_index < 0:
                    curr_set_list[secode_position_dict[secode]] = '待观察'
                    continue
   
                amount          = self.secode_hist_data[secode][cur_index][6]
                today_close     = self.secode_hist_data[secode][cur_index][2]  
                today_chg       = self.secode_hist_data[secode][cur_index][5]
                high_price      = self.secode_highprice_dict[secode][cur_index]
                curr_fall_value = (today_close - high_price) / high_price

                curr_set_list[secode_position_dict[secode]] = '待观察'
                curr_close_list[secode_position_dict[secode]] = today_close
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price

                if amount != 0:                    
                    if curr_fall_value < fall_value:
                        curr_delete_unobserve_list.append(secode)
                        maximum_price = high_price
                        minimum_price = today_close
                        curr_add_observe_dict[secode] = [maximum_price, minimum_price]
                        curr_set_list[secode_position_dict[secode]] = '观察'
                    else:
                        curr_set_list[secode_position_dict[secode]] = '待观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '待观察'

            for secode in observe_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                high_price   = self.secode_highprice_dict[secode][cur_index]

                curr_set_list[secode_position_dict[secode]] = '观察'
                curr_close_list[secode_position_dict[secode]] = today_close
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price
                
                if amount != 0:                                        
                    if observe_dict[secode][1] > today_close:
                        observe_dict[secode][1] = today_close          

                    maximum_price = float(observe_dict[secode][0])
                    minimum_price = float(observe_dict[secode][1])
                    init_fall_value = (minimum_price - maximum_price) / maximum_price                    
                    rebound_rise_value = init_fall_value * k1 

                    if today_close > minimum_price * (1 + rebound_rise_value):
                        rebound_maximum_price = today_close
                        curr_delete_observe_list.append(secode)
                        if today_chg >= 0.09:
                            rise_stop_count += 1
                            curr_set_list[secode_position_dict[secode]] = '当日涨停，继续等待次日买入'
                            curr_add_wait_buy_dict[secode] = [rebound_maximum_price, minimum_price, init_fall_value]
                        else:
                            curr_buy_count += 1
                            curr_earning += self.trade_cost
                            curr_earning_list[secode_position_dict[secode]] = self.trade_cost                                
                            curr_set_list[secode_position_dict[secode]] = '直接买入，放入持仓'
                            curr_add_hold_dict[secode] = [rebound_maximum_price, minimum_price, init_fall_value] # 记录总降幅与最新的最高价
                    else:
                        curr_set_list[secode_position_dict[secode]] = '观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '观察'

            for secode in wait_buy_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]   
                high_price   = self.secode_highprice_dict[secode][cur_index]
                curr_set_list[secode_position_dict[secode]] = '等待买入'         
                curr_close_list[secode_position_dict[secode]] = today_close      
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price

                if amount != 0:                                    
                    if today_close > wait_buy_dict[secode][0]:
                        wait_buy_dict[secode][0] = today_close                    
                    if today_close < wait_buy_dict[secode][1]:
                        wait_buy_dict[secode][1] = today_close     

                    if today_chg >= 0.09:       
                        rise_stop_count += 1
                        curr_set_list[secode_position_dict[secode]] = '再次涨停,继续等待买入'     
                    else:
                        curr_delete_wait_buy_list.append(secode)
                        maximum_price = wait_buy_dict[secode][0]
                        minimum_price = wait_buy_dict[secode][1]   
                        init_fall_value = wait_buy_dict[secode][2]
                        curr_rise_value = (maximum_price - minimum_price) / minimum_price

                        rebound_fall_value = init_fall_value * k2 + curr_rise_value * k3

                        if today_close < float(maximum_price) * (1 + rebound_fall_value):
                            curr_add_observe_dict[secode] = [max(maximum_price, high_price), minimum_price]
                            curr_set_list[secode_position_dict[secode]] = '跌破止损, 放入观察集'
                        else:
                            curr_add_hold_dict[secode] = [maximum_price, minimum_price, init_fall_value]
                            curr_buy_count += 1
                            curr_earning += self.trade_cost
                            curr_earning_list[secode_position_dict[secode]] = self.trade_cost     
                            curr_set_list[secode_position_dict[secode]] = '买入，放入持仓'    
                else:
                    curr_set_list[secode_position_dict[secode]] = '等待买入'    

            for secode in hold_dict:
                cur_index       = start_index - secode_startindex_dict[secode]     
                amount          = self.secode_hist_data[secode][cur_index][6]
                today_close     = self.secode_hist_data[secode][cur_index][2]  
                today_chg       = self.secode_hist_data[secode][cur_index][5]   
                high_price      = self.secode_highprice_dict[secode][cur_index]
                curr_rebound_fall_value = (today_close - high_price) / high_price

                curr_set_list[secode_position_dict[secode]] = '持仓' 
                curr_close_list[secode_position_dict[secode]] = today_close   
                curr_change_list[secode_position_dict[secode]] = today_chg     
                curr_high_price_list[secode_position_dict[secode]] = high_price

                hold_timecount += 1     
                if amount != 0:                    
                    curr_earning += float(today_chg)
                    curr_earning_list[secode_position_dict[secode]] = today_chg        

                    if today_close > hold_dict[secode][0]:
                        hold_dict[secode][0] = today_close

                    rebound_maximum_price = hold_dict[secode][0]
                    rebound_minimum_price = hold_dict[secode][1]
                    init_fall_value = hold_dict[secode][2]
                    curr_rise_value = (rebound_maximum_price - rebound_minimum_price) / rebound_minimum_price
                    rebound_fall_value = init_fall_value * k2 + curr_rise_value * k3                    

                    if today_close < rebound_maximum_price * (1 + rebound_fall_value):
                        maximum_price = rebound_maximum_price
                        minimum_price = today_close
                        curr_delete_hold_list.append(secode)
                        if today_chg <= -0.09:
                            fall_stop_count += 1
                            curr_add_wait_sale_dict[secode] = [maximum_price, minimum_price, rebound_minimum_price, init_fall_value]                            
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,但跌停,等待次日卖出'

                        elif curr_rebound_fall_value <= fall_value:
                            curr_add_observe_dict[secode] = [max(maximum_price, high_price), minimum_price]
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,放入观察集合'
                        else:
                            curr_add_unobserve_dict[secode] = hold_dict[secode]
                            curr_set_list[secode_position_dict[secode]] = '当日卖出,放入待观察集合'
                else:
                    curr_set_list[secode_position_dict[secode]] = '持仓'      

            for secode in wait_sale_dict:
                cur_index    = start_index - secode_startindex_dict[secode]     
                amount       = self.secode_hist_data[secode][cur_index][6]
                today_close  = self.secode_hist_data[secode][cur_index][2]  
                today_chg    = self.secode_hist_data[secode][cur_index][5]  
                high_price   = self.secode_highprice_dict[secode][cur_index] 
                curr_set_list[secode_position_dict[secode]] = '等待卖出'   
                curr_close_list[secode_position_dict[secode]] = today_close   
                curr_change_list[secode_position_dict[secode]] = today_chg
                curr_high_price_list[secode_position_dict[secode]] = high_price

                hold_timecount += 1      
                if amount != 0:                         
                    curr_earning += float(today_chg)
                    curr_earning_list[secode_position_dict[secode]] = today_chg

                    if today_close > wait_sale_dict[secode][0]:
                        wait_sale_dict[secode][0] = today_close                    
                    if today_close < wait_sale_dict[secode][1]:
                        wait_sale_dict[secode][1] = today_close

                    if today_chg <= -0.09:
                        curr_set_list[secode_position_dict[secode]] = '当日跌停，继续等待次日卖出'
                        fall_stop_count += 1
                    else:
                        curr_delete_wait_sale_list.append(secode)
                        maximum_price = wait_sale_dict[secode][0]
                        minimum_price = wait_sale_dict[secode][1]

                        rebound_maximum_price = wait_sale_dict[secode][0]
                        rebound_minimum_price = wait_sale_dict[secode][2]
                        init_fall_value = wait_sale_dict[secode][3]
                        curr_rise_value = (rebound_maximum_price - rebound_minimum_price) / rebound_maximum_price
                        rebound_fall_value = init_fall_value * k2 + curr_rise_value * k3  

                        if today_close >= float(maximum_price) * (1 + rebound_fall_value):
                            curr_add_hold_dict[secode] = [maximum_price, rebound_minimum_price, init_fall_value]                   
                            curr_set_list[secode_position_dict[secode]] = '卖出当日涨回止损，放入持仓'
                        else:
                            curr_add_observe_dict[secode] = [max(maximum_price, high_price), minimum_price]
                            curr_set_list[secode_position_dict[secode]] = '卖出，放入观察'
                else:
                    curr_set_list[secode_position_dict[secode]] = '等待卖出'                                          

            if len(hold_dict) + len(wait_sale_dict) + curr_buy_count != 0:
                curr_earning /= (len(hold_dict) + len(wait_sale_dict) + curr_buy_count)

            remove_list_item(unobserve_list, curr_delete_unobserve_list)
            remove_dict_item(observe_dict, curr_delete_observe_list)
            remove_dict_item(wait_buy_dict, curr_delete_wait_buy_list)
            remove_dict_item(hold_dict, curr_delete_hold_list)
            remove_dict_item(wait_sale_dict, curr_delete_wait_sale_list)

            add_list_item(unobserve_list, curr_add_unobserve_dict)
            add_dict_item(observe_dict, curr_add_observe_dict)
            add_dict_item(wait_buy_dict, curr_add_wait_buy_dict)
            add_dict_item(hold_dict, curr_add_hold_dict)
            add_dict_item(wait_sale_dict, curr_add_wait_sale_dict)

            date_list.append(self.date_data[start_index][0])
            earning_list.append(float(curr_earning))
            curr_earning_list.append(curr_earning)
            curr_earning_list.insert(0, self.date_data[start_index][0])
            curr_set_list.insert(0, self.date_data[start_index][0])
            curr_close_list.insert(0, self.date_data[start_index][0])
            curr_change_list.insert(0, self.date_data[start_index][0])
            curr_high_price_list.insert(0, self.date_data[start_index][0])

            #记录每支股票的收益，集合属性:
            secode_earning_matrix.append(curr_earning_list)
            secode_set_matrix.append(curr_set_list)
            secode_close_matrix.append(curr_close_list)
            secode_chg_matrix.append(curr_change_list)
            secode_high_price_matrix.append(curr_high_price_list)

            start_index += 1

        result = []
        result.append(date_list)
        result.append(earning_list)
        result.append(secode_earning_matrix)
        result.append(secode_set_matrix)
        result.append(secode_close_matrix)
        result.append(secode_chg_matrix)
        result.append(secode_high_price_matrix)
        # result.append((rise_stop_count + fall_stop_count)/hold_timecount)

        # print('rise_stop_count: %d, fall_stop_count: %d, sum: %d, hold_timecount: %d '\
        #      % (rise_stop_count, fall_stop_count, rise_stop_count + fall_stop_count, hold_timecount))
        return result

    def compute_daily_result_atom(self, fall_value, rebound_rise_value, rebound_fall_value):
        if self.trade_type == 'today_simple':
            return self.compute_daily_result_close_todaytrade_simple(fall_value, rebound_rise_value, rebound_fall_value)
                
        if self.trade_type == 'today':
            return self.compute_daily_result_close_todaytrade(fall_value, rebound_rise_value, rebound_fall_value)     

        if self.trade_type == 'next_day':
            return self.compute_daily_result_close_nextday(fall_value, rebound_rise_value, rebound_fall_value)  

        if self.trade_type == 'today_improve':       
            return self.compute_daily_result_close_todaytrade_improve(fall_value, rebound_rise_value, rebound_fall_value)

    def compute_daily_result(self, fall_value_list, rebound_rise_value_list, rebound_fall_value_list):        
        for fall_value in fall_value_list:     
            for rebound_rise_value in rebound_rise_value_list:        
                for rebound_fall_value in rebound_fall_value_list:                
                    condition_str = '%d_%.2f_%.2f_%.2f' % \
                                    (len(self.secode_list), fall_value, rebound_rise_value, rebound_fall_value)     

                    file_name = self.dir_name + condition_str
                    result = self.compute_daily_result_atom(fall_value, rebound_rise_value, rebound_fall_value)                                                     
                    curr_earning_netvalue = self.analyze_result(result, file_name)  

                    self.lock.acquire()
                    self.sum_result.append([condition_str, curr_earning_netvalue])             
                    self.complete_count += 1
                    self.log_info('%s, %d complete, %d left!\n' % \
                                (condition_str, self.complete_count, self.sum_compute_count - self.complete_count))  
                    self.lock.release()      

    def set_work_thread(self):
        starttime = datetime.datetime.now()
        info_str = '开始时间: %s \n' % (starttime.strftime("%Y-%m-%d %H:%M:%S"))
        self.log_info(info_str)     

        for fall_value in self.fall_value_list:
            tmp_thread = threading.Thread(target=self.compute_daily_result, args=([fall_value], \
                                        self.rebound_rise_value_list, self.rebound_fall_value_list, ))
            self.thread_list.append(tmp_thread)

        for thread in self.thread_list:
            thread.start()

        for thread in self.thread_list:
            thread.join()

        sum_file_name = self.dir_name + 'sum_%d.xlsx' %(len(self.secode_list)) 
        sum_result = self.trans_sum_result(self.sum_result)     
        self.excel_obj.check_file(sum_file_name)      
        self.excel_obj.write_all_data(oridata = sum_result, file_name = sum_file_name, \
                                        sheetname= 'sum_net_value', style="ori")
        
        endtime = datetime.datetime.now()
        costTime = (endtime - starttime).seconds
        info_str = "\n结束时间: %s, 耗费: %ds\n" % (endtime.strftime("%Y-%m-%d %H:%M:%S"), costTime)
        self.log_info(info_str)               

    def compute_main(self):
        self.main_starttime = datetime.datetime.now()
        info_str = '开始时间: %s \n' % (self.main_starttime.strftime("%Y-%m-%d %H:%M:%S"))
        self.log_info(info_str)    
        self.step_starttime = self.main_starttime
         
        for fall_value in self.fall_value_list:     
            for rebound_rise_value in self.rebound_rise_value_list:        
                for rebound_fall_value in self.rebound_fall_value_list:                
                    condition_str = '%d_%.2f_%.2f_%.2f' % \
                                    (len(self.secode_list), fall_value, rebound_rise_value, rebound_fall_value)     

                    result = self.compute_daily_result_atom(fall_value, rebound_rise_value, rebound_fall_value)
                    self.date_list = result[0]
                    self.analyze_result(result, condition_str)  
 
                    self.complete_count += 1
                    self.step_endtime = datetime.datetime.now()
                    cost_seconds = (self.step_endtime - self.step_starttime).seconds
                    self.log_info('%s, %d complete, %d left!, cost seconds: %d \n' % \
                                (condition_str, self.complete_count, \
                                self.sum_compute_count - self.complete_count, cost_seconds))  
                    self.step_starttime = self.step_endtime

        self.save_sum_result()                                  
        self.main_endtime = datetime.datetime.now()
        costTime = (self.main_endtime - self.main_starttime).seconds
        info_str = "\n结束时间: %s, 耗费: %ds\n" % (self.main_endtime.strftime("%Y-%m-%d %H:%M:%S"), costTime)
        self.log_info(info_str)     
        
    def compute_main_B(self):
        self.main_starttime = datetime.datetime.now()
        info_str = '开始时间: %s \n' % (self.main_starttime.strftime("%Y-%m-%d %H:%M:%S"))
        self.log_info(info_str)    
        self.step_starttime = self.main_starttime
         
        for fall_value in self.fall_value_list:     
            for k1 in self.k1_list:        
                for k2 in self.k2_list: 
                    for k3 in self.k3_list:               
                    condition_str = '%d_%.2f_%.2f_%.2f_%.2f' %  (len(self.secode_list), fall_value, k1, k2, k3)     

                    result = self.compute_todaytrade_improve_B(fall_value, k1, k2, k3)
                    self.date_list = result[0]
                    self.analyze_result(result, condition_str)  
 
                    self.complete_count += 1
                    self.step_endtime = datetime.datetime.now()
                    cost_seconds = (self.step_endtime - self.step_starttime).seconds
                    self.log_info('%s, %d complete, %d left!, cost seconds: %d \n' % \
                                (condition_str, self.complete_count, \
                                self.sum_compute_count - self.complete_count, cost_seconds))  
                    self.step_starttime = self.step_endtime

        self.save_sum_result()                                  
        self.main_endtime = datetime.datetime.now()
        costTime = (self.main_endtime - self.main_starttime).seconds
        info_str = "\n结束时间: %s, 耗费: %ds\n" % (self.main_endtime.strftime("%Y-%m-%d %H:%M:%S"), costTime)
        self.log_info(info_str)     

    def get_index_earning(self, index_code):
        column_str = ' PCTCHG '
        result =  self.database_obj.get_histdata_by_date(startdate=self.data_start_date, enddate=self.data_end_date, \
                                                                    table_name=index_code, cloumn_str=column_str)
        return result

    def save_sum_result(self):
        simple_title = ['参数条件 指标', '绝对年化收益率', '最大回撤', '绝对年化收益回撤比', \
                        '相对沪深300年化收益率', '最大回撤',  '相对年化收益回撤比']
        self.sum_result[0] = self.trans_sum_result(self.sum_result[0])
        self.sum_result[0].insert(0, simple_title)

        comp_title = ['时间 参数条件']
        for date in self.date_list:
            comp_title.append(date)

        self.sum_result[1].insert(0, comp_title)
        self.sum_result[2].insert(0, comp_title)
        self.sum_result[3].insert(0, comp_title)
        self.sum_result[4].insert(0, comp_title)
        self.sum_result[5].insert(0, comp_title)
        self.sum_result[6].insert(0, comp_title)                

        self.sum_result[1] = trans_matrix(self.sum_result[1])
        self.sum_result[2] = trans_matrix(self.sum_result[2])
        self.sum_result[3] = trans_matrix(self.sum_result[3])
        self.sum_result[4] = trans_matrix(self.sum_result[4])
        self.sum_result[5] = trans_matrix(self.sum_result[5])
        self.sum_result[6] = trans_matrix(self.sum_result[6])                

        file_info = ''
        if len(self.fall_value_list) == 1:
            file_info += "_A_%.2f" % (self.fall_value_list[0])
        
        if len(self.rebound_rise_value_list) == 1:
            file_info += "_B_%.2f" % (self.rebound_rise_value_list[0])

        if len(self.rebound_fall_value_list) == 1:
            file_info += "_C_%.2f" % (self.rebound_fall_value_list[0])

        sum_file_name = self.dir_name + 'sum_%d_%d%s.xlsx' %(self.sum_compute_count, len(self.secode_list), file_info)   

        self.excel_obj.check_file(sum_file_name)   

        self.excel_obj.write_all_data(oridata = self.sum_result[0], file_name = sum_file_name, \
                                        sheetname= 'sum_value', style="ori")
        print('写入 sum_value')

        self.excel_obj.write_all_data(oridata = self.sum_result[1], file_name = sum_file_name, \
                                        sheetname= 'earning', style="ori")
        print('写入 earning')

        self.excel_obj.write_all_data(oridata = self.sum_result[2], file_name = sum_file_name, \
                                        sheetname= 'netvalue', style="ori")
        print('写入 netvalue')

        self.excel_obj.write_all_data(oridata = self.sum_result[3], file_name = sum_file_name, \
                                        sheetname= 'retrancement', style="ori")   
        print('写入 retrancement')

        # self.excel_obj.write_all_data(oridata = self.sum_result[4], file_name = sum_file_name, \
        #                                 sheetname= 'hedged_earning', style="ori")
        # print('写入 hedged_earning')

        # self.excel_obj.write_all_data(oridata = self.sum_result[5], file_name = sum_file_name, \
        #                                 sheetname= 'hedged_netvalue', style="ori")
        # print('写入 hedged_netvalue')

        # self.excel_obj.write_all_data(oridata = self.sum_result[6], file_name = sum_file_name, \
        #                                 sheetname= 'hedged_retrancement', style="ori") 
        # print('写入 hedged_retrancement')                                            

    def get_secode_position(self, secode_list):
        result = {}
        index = 0
        while index < len(secode_list):
            secode = secode_list[index]
            result[secode] = index
            index += 1
        return result

    def get_init_set_list(self, secode_numb):
        result = []
        i = 0
        while i < secode_numb:
            result.append('待观察')
            i += 1
        return result
    
    def get_init_earning_list(self, secode_numb):
        result = []
        i = 0
        while i < secode_numb:
            result.append(0)
            i += 1
        return result        

    def get_earning_matrix_title(self, secode_list):
        result = ['股票收益']
        for item in secode_list:
            result.append(item)
        result.append('合计')
        return result

    def get_set_matrix_title(self, secode_list):
        result = ['股票集合属性']
        for item in secode_list:
            result.append(item)
        return result        
        
    def get_close_matrix_title(self, secode_list):
        result = ['收盘价']
        for item in secode_list:
            result.append(item)
        return result            

    def get_change_matrix_title(self, secode_list):
        result = ['当日涨跌幅']
        for item in secode_list:
            result.append(item)
        return result             

    def get_high_price_matrix_title(self, secode_list):
        result = ['新高']
        for item in secode_list:
            result.append(item)
        return result             
        
    def trans_sum_result(self, ori_data):
        ab_max_netvalue = -10
        ab_index = 0

        ab_max_retrancement = -10
        ab_max_re_index = 0

        ab_max_return_retrancement = -10
        ab_max_rere_index = 0        

        re_max_netvalue =-10
        re_index = 0

        re_max_retrancement = -10
        re_max_re_index = 0

        re_max_return_retrancement = -10
        re_max_rere_index = 0

        index = 0
        while index < len(ori_data):
            item = ori_data[index]
            if item[1] > ab_max_netvalue and item[1] != 0:
                ab_max_netvalue = item[1]
                ab_index = index

            if item[2] > ab_max_retrancement and item[2] != 0:
                ab_max_retrancement = item[2]
                ab_max_re_index = index

            if item[3] > ab_max_return_retrancement and item[3] != 0:
                ab_max_return_retrancement = item[3]
                ab_max_rere_index = index

            if item[4] > re_max_netvalue and item[4] != 0: 
                re_max_netvalue = item[4]
                re_index = index

            if item[5] > re_max_retrancement and item[5] != 0:
                re_max_retrancement = item[5]
                re_max_re_index = index

            if item[6] > re_max_return_retrancement and item[6] != 0:
                re_max_return_retrancement = item[6]
                re_max_rere_index = index

            index += 1

        ori_data.append(['最大绝对年化收益值: ', ori_data[ab_index][1],  ori_data[ab_index][0]])
        ori_data.append(['最小的绝对最大回撤: ', ori_data[ab_max_re_index][2],  ori_data[ab_max_re_index][0]])
        ori_data.append(['最大绝对年化收益回撤比: ', ori_data[ab_max_rere_index][3], ori_data[ab_max_rere_index][0]])
        ori_data.append(['最大相对年化收益值: ', ori_data[re_index][4], ori_data[re_index][0]])
        ori_data.append(['最小的相对最大回撤: ', ori_data[re_max_re_index][5],  ori_data[re_max_re_index][0]])
        ori_data.append(['最大相对年化收益回撤比: ', ori_data[re_max_rere_index][6], ori_data[re_max_rere_index][0]])
        return ori_data
    
    def trans_single_result(self, ori_data):
        max_earning = ori_data[0][1]
        max_earning_date = ori_data[0][0]
        max_retracement = ori_data[0][2]
        max_retracement_date = ori_data[0][0]

        for item in ori_data:
            if max_earning < item[1]:
                max_earning = item[1]
                max_earning_date = item[0]

            if max_retracement > item[2]:
                max_retracement = item[2]
                max_retracement_date = item[0]
        
        ori_data.append(['最大值: ', max_earning, max_retracement])
        ori_data.append(['对应日期: ', max_earning_date, max_retracement_date])
        return ori_data

    def add_statistic(self, oridata_list):
        data_np = np.array(oridata_list)
        oridata_list.append(data_np.mean())
        oridata_list.append(data_np.max())
        oridata_list.append(data_np.min())
        oridata_list.append(data_np.std())
        return oridata_list

    def analyze_result(self, result, condition_str):
        if 'today_improve' == self.trade_type:
            return self.analyze_today_trade_result_improve(result, condition_str)

        if 'today' == self.trade_type or 'today_simple' == self.trade_type:
            return self.analyze_today_trade_result(result, condition_str)
        
        if 'next_day' in self.trade_type:
            return self.analyze_nextday_trade_result(result, condition_str)

    def analyze_today_trade_result_improve(self, result, condition_str):
        date_list = result[0]
        earning_list = result[1]
        secode_earning_matrix = result[2]
        secode_set_matrix = result[3]
        secode_close_matrix = result[4]
        secode_chg_matrix = result[5]
        secode_high_price_matrix = result[6]
        secode_fall_value_matrix = self.get_fall_value_matrix(secode_close_matrix, secode_high_price_matrix)

                
        earning_netvalue = compute_netvalue(earning_list)
        retrancement_value = compute_retrancemnet(earning_netvalue)
        annualized_return = get_annualized_return(earning_netvalue)
        max_retracement = min(retrancement_value)

        hedged_earning_list = self.get_hedged_earning_list(earning_list, self.get_index_earning(self.index_code))
        hedged_earning_netvalue = compute_netvalue(hedged_earning_list)
        hedged_retrancement_value = compute_retrancemnet(hedged_earning_netvalue)
        hedged_annualized_return = get_annualized_return(hedged_earning_netvalue)
        hedged_max_retracement = min(hedged_retrancement_value)


        if self.sum_compute_count < 10:            
            excel_data = []
            for i in range(len(date_list)):
                excel_data.append([date_list[i], earning_netvalue[i], retrancement_value[i]])

            file_name = self.dir_name + condition_str
            excel_data = self.trans_single_result(excel_data)
            excel_file_name = file_name + '.xlsx'
            self.excel_obj.check_file(excel_file_name)        
            self.excel_obj.write_all_data(oridata = excel_data, \
                                        file_name = excel_file_name, sheetname= 'net_value', style="ori") 
            if len(self.secode_list) < 10:                             
                self.excel_obj.write_all_data(oridata = secode_earning_matrix, \
                                            file_name = excel_file_name, sheetname='earning', style="ori")

                self.excel_obj.write_all_data(oridata = secode_set_matrix, \
                                            file_name = excel_file_name, sheetname='set', style="ori")

                self.excel_obj.write_all_data(oridata = secode_high_price_matrix, \
                                            file_name = excel_file_name, sheetname='high_price', style="ori")                                        

                self.excel_obj.write_all_data(oridata = secode_close_matrix, \
                                                file_name = excel_file_name, sheetname= 'close', style="ori")   

                self.excel_obj.write_all_data(oridata = secode_fall_value_matrix, \
                                                file_name = excel_file_name, sheetname= 'fall_value', style="ori")                                                     

                # self.excel_obj.write_all_data(oridata = secode_chg_matrix, \
                #                                 file_name = excel_file_name, sheetname= 'change', style="ori")                                                                                       

            draw_datanumb = len(date_list)
            self.lock.acquire()
            self.draw_one_pic(earning_netvalue, retrancement_value, date_list[0:draw_datanumb], file_name+'_ori')
            self.draw_one_pic(hedged_earning_netvalue, hedged_retrancement_value, date_list[0:draw_datanumb], file_name+'_hedged')
            self.lock.release()        

        earning_list.insert(0, condition_str)
        earning_netvalue.insert(0, condition_str)
        retrancement_value.insert(0, condition_str)
        
        hedged_earning_list.insert(0, condition_str)
        hedged_earning_netvalue.insert(0, condition_str)
        hedged_retrancement_value.insert(0, condition_str)
        
        print('annualized_return: %.4f, max_retracement: %.4f, hedged_annualized_return: %.4f, hedged_max_retracement: %.4f' % \
            (annualized_return, max_retracement, hedged_annualized_return, hedged_max_retracement))

        abs_rate = 0
        if abs(max_retracement) != 0:
            abs_rate = annualized_return / abs(max_retracement)
        hedged_rate = 0
        if abs(hedged_max_retracement) != 0:
            hedged_rate = hedged_annualized_return / abs(hedged_max_retracement)

        self.sum_result[0].append([condition_str, annualized_return, max_retracement, abs_rate , \
                                    hedged_annualized_return, hedged_max_retracement, hedged_rate])
        self.sum_result[1].append(earning_list)  
        self.sum_result[2].append(earning_netvalue)       
        self.sum_result[3].append(retrancement_value)   
        
        self.sum_result[4].append(hedged_earning_list)  
        self.sum_result[5].append(hedged_earning_netvalue)       
        self.sum_result[6].append(hedged_retrancement_value)  

    def analyze_today_trade_result(self, result, condition_str):
        date_list = result[0]
        earning_list = result[1]
        secode_earning_matrix = result[2]
        secode_set_matrix = result[3]
        secode_close_matrix = result[4]
        secode_chg_matrix = result[5]
        rise_fall_stop_percent = result[len(result)-1]
                
        earning_netvalue = compute_netvalue(earning_list)
        retrancement_value = compute_retrancemnet(earning_netvalue)
        annualized_return = get_annualized_return(earning_netvalue)
        max_retracement = min(retrancement_value)

        hedged_earning_list = self.get_hedged_earning_list(earning_list, self.get_index_earning(self.index_code))
        hedged_earning_netvalue = compute_netvalue(hedged_earning_list)
        hedged_retrancement_value = compute_retrancemnet(hedged_earning_netvalue)
        hedged_annualized_return = get_annualized_return(hedged_earning_netvalue)
        hedged_max_retracement = min(hedged_retrancement_value)


        if self.sum_compute_count < 5:            
            excel_data = []
            for i in range(len(date_list)):
                excel_data.append([date_list[i], earning_netvalue[i], retrancement_value[i]])

            file_name = self.dir_name + condition_str
            excel_data = self.trans_single_result(excel_data)
            excel_file_name = file_name + '.xlsx'
            self.excel_obj.check_file(excel_file_name)        
            self.excel_obj.write_all_data(oridata = excel_data, \
                                        file_name = excel_file_name, sheetname= 'net_value', style="ori") 
            if len(self.secode_list) < 10:                             
                self.excel_obj.write_all_data(oridata = secode_earning_matrix, \
                                            file_name = excel_file_name, sheetname='earning', style="ori")

                self.excel_obj.write_all_data(oridata = secode_set_matrix, \
                                            file_name = excel_file_name, sheetname='set', style="ori")                                                   

                # self.excel_obj.write_all_data(oridata = secode_chg_matrix, \
                #                                 file_name = excel_file_name, sheetname= 'change', style="ori")                                                                                       

            draw_datanumb = len(date_list)
            self.lock.acquire()
            self.draw_one_pic(earning_netvalue, retrancement_value, date_list[0:draw_datanumb], file_name+'_ori')
            self.draw_one_pic(hedged_earning_netvalue, hedged_retrancement_value, date_list[0:draw_datanumb], file_name+'_hedged')
            self.lock.release()        

        earning_list.insert(0, condition_str)
        earning_netvalue.insert(0, condition_str)
        retrancement_value.insert(0, condition_str)
        
        hedged_earning_list.insert(0, condition_str)
        hedged_earning_netvalue.insert(0, condition_str)
        hedged_retrancement_value.insert(0, condition_str)
        
        print('annualized_return: %.4f, max_retracement: %.4f, hedged_annualized_return: %.4f, hedged_max_retracement: %.4f' % \
            (annualized_return, max_retracement, hedged_annualized_return, hedged_max_retracement))

        self.sum_result[0].append([condition_str, annualized_return, max_retracement, \
                                hedged_annualized_return, hedged_max_retracement, rise_fall_stop_percent])
        self.sum_result[1].append(earning_list)  
        self.sum_result[2].append(earning_netvalue)       
        self.sum_result[3].append(retrancement_value)   
        
        self.sum_result[4].append(hedged_earning_list)  
        self.sum_result[5].append(hedged_earning_netvalue)       
        self.sum_result[6].append(hedged_retrancement_value)              

    def analyze_nextday_trade_result(self, result, condition_str):
        date_list = result[0]
        buy_earning_list = result[1]
        hold_earning_list = result[2]        
        sale_earning_list = result[3]
        all_earning_list = result[4]
        secode_set_matrix = result[5]
                
        netvalue_list = compute_netvalue(all_earning_list)
        target_value = netvalue_list[len(netvalue_list)-1]

        date_list.append('平均值: ')
        date_list.append('最大值: ')
        date_list.append('最小值: ')
        date_list.append('标准差: ')
        buy_earning_list = self.add_statistic(buy_earning_list)
        hold_earning_list = self.add_statistic(hold_earning_list)
        sale_earning_list = self.add_statistic(sale_earning_list)
        all_earning_list = self.add_statistic(all_earning_list)
        netvalue_list = self.add_statistic(netvalue_list)

        write_data = []
        for i in range(len(date_list)):
            write_data.append([date_list[i], buy_earning_list[i], hold_earning_list[i], \
                                sale_earning_list[i], all_earning_list[i], netvalue_list[i]])
        file_name = self.dir_name + condition_str
        excel_file_name = file_name + '.xlsx'
        self.excel_obj.check_file(excel_file_name)  
        self.excel_obj.write_all_data(oridata = write_data, file_name = excel_file_name, sheetname= 'earning', style="ori")
        if len(self.secode_list) < 3:
            self.excel_obj.write_all_data(oridata = secode_set_matrix, file_name = excel_file_name, sheetname= 'set', style="ori")

        draw_datanumb = len(buy_earning_list) - 4
        self.draw_four_pic(buy_earning_list[0:draw_datanumb], hold_earning_list[0:draw_datanumb], \
                            sale_earning_list[0:draw_datanumb], all_earning_list[0:draw_datanumb], date_list[0:draw_datanumb], \
                            file_name)
        return target_value

    def get_fall_value_matrix(self, close_matrix, high_price_matrix):
        result = []
        title = ['降幅']
        for secode in self.secode_list:
            title.append(secode)
        result.append(title)
        
        row_index = 1
        while row_index < len(close_matrix):
            curr_row = [close_matrix[row_index][0]]
            col_index = 1
            while col_index < len(close_matrix[row_index]):
                curr_close = close_matrix[row_index][col_index]
                curr_high_price = high_price_matrix[row_index][col_index]
                if curr_high_price != 0:
                    curr_fall_value = (curr_close-curr_high_price) / curr_high_price
                else:
                    curr_fall_value = 0                
                curr_row.append(curr_fall_value)                
                col_index += 1
            result.append(curr_row)
            row_index += 1
        return result

    def get_hedged_earning_list(self, ori_earning_list, index_earning_list):
        result = []
        index = 0
        while index < len(ori_earning_list):
            if float(ori_earning_list[index]) != 0:
                result.append(float(ori_earning_list[index]) - float(index_earning_list[index][0]))
            else:
                result.append(0)
            index += 1
        return result

    def draw_one_pic(self, earning_netvalue, earning_retrancement, date_list, file_name):
        self.figure_count = 0
        plt.figure(self.figure_count)

        date_x = []
        for date in date_list: 
            trans_date = datetime.datetime.strptime(str(date), '%Y%m%d').date() 
            date_x.append(trans_date)            

        plt.plot(date_x, earning_netvalue, label='net value')
        plt.plot(date_x, earning_retrancement, label='retracement')
        plt.xlabel('Time')
        plt.ylabel('Earning Rate')
        plt.title('All Earing')

        png_file_name = file_name + '.png'
        plt.savefig(png_file_name)
        plt.cla()
        # plt.show()
        
    def draw_four_pic(self, buy_earning_list, hold_earning_list, \
                    sale_earning_list, all_earning_list, date_list, file_name):
        self.figure_count = 0
        plt.figure(self.figure_count)

        date_x = []
        for date in date_list: 
            trans_date = datetime.datetime.strptime(str(date), '%Y%m%d').date() 
            date_x.append(trans_date)        

        plt.subplot(2,2,1)
        buy_earning_netvalue = compute_netvalue(buy_earning_list)
        buy_earning_retrancement = compute_retrancemnet(buy_earning_netvalue)
        plt.plot(date_x, buy_earning_netvalue, label='net value')
        plt.plot(date_x, buy_earning_retrancement, label='retracement')
        plt.xlabel('Time')
        plt.ylabel('Earning Rate')
        plt.title('Buy Earing')

        hold_earning_netvalue = compute_netvalue(hold_earning_list)
        hold_earning_retracement = compute_retrancemnet(hold_earning_netvalue)
        plt.subplot(2,2,2)
        plt.plot(date_x, hold_earning_netvalue, label='net value')
        plt.plot(date_x, hold_earning_retracement, label='retracement')
        plt.xlabel('Time')
        plt.ylabel('Earning Rate')
        plt.title('Hold Earing')

        sale_earning_netvalue = compute_netvalue(sale_earning_list)
        sale_earning_retracement = compute_retrancemnet(sale_earning_netvalue)
        plt.subplot(2,2,3)
        plt.plot(date_x, sale_earning_netvalue, label='net value')
        plt.plot(date_x, sale_earning_retracement, label='retracement')
        plt.xlabel('Time')
        plt.ylabel('Earning Rate')
        plt.title('Sale Earing')

        plt.subplot(2,2,4)
        all_earning_netvalue = compute_netvalue(all_earning_list)
        all_earning_retracement = compute_retrancemnet(all_earning_netvalue)
        plt.plot(date_x, all_earning_netvalue, label='net value')
        plt.plot(date_x, all_earning_retracement, label='retracement')
        plt.xlabel('Time')
        plt.ylabel('Earning Rate')
        plt.title('All Earing')

        # plt.show()        
        
        png_file_name = file_name + '.png'
        plt.savefig(png_file_name)

        plt.cla()

def get_today_improve_params_20():
    # # 初始测试区间
    # fall_value_list = create_array(-1, -3, -79)
    # rebound_rise_value_list = create_array(1, 3, 29)
    # rebound_fall_value_list = create_array(-1, -3, -19)

    # 最大绝对年化收益值: 
    fall_value_list = [-0.61]
    rebound_rise_value_list = [0.07]
    rebound_fall_value_list = [-0.01]    

    # # 最大绝对年化收益回撤比:  
    # fall_value_list = [-0.61]
    # rebound_rise_value_list = [0.04]
    # rebound_fall_value_list = [-0.04]    

    # # 最小的绝对最大回撤:  
    # fall_value_list = [-0.79]
    # rebound_rise_value_list = [0.22]
    # rebound_fall_value_list = [-0.01]    

    # # 最大相对年化收益值, 最大相对年化收益回撤比: 
    # fall_value_list = [-0.61]
    # rebound_rise_value_list = [0.10]
    # rebound_fall_value_list = [-0.01]      

    # # 最小的相对最大回撤: 
    # fall_value_list = [-0.79]
    # rebound_rise_value_list = [0.19]
    # rebound_fall_value_list = [-0.01]    

    return  fall_value_list, rebound_rise_value_list, rebound_fall_value_list

def get_today_improve_params_30():
    # 初始测试区间
    # fall_value_list = create_array(-1, -3, -79)
    # rebound_rise_value_list = create_array(1, 3, 29)
    # rebound_fall_value_list = create_array(-1, -3, -19)

    # 最大绝对年化收益值: 
    fall_value_list = [-0.67]
    rebound_rise_value_list = [0.04]
    rebound_fall_value_list = [-0.07]    

    # 最小的绝对最大回撤, 最大绝对年化收益回撤比:
    fall_value_list = [-0.76]
    rebound_rise_value_list = [0.19]
    rebound_fall_value_list = [-0.01]    

    # 最大相对年化收益值:  
    fall_value_list = [-0.61]
    rebound_rise_value_list = [0.10]
    rebound_fall_value_list = [-0.07]    

    # 最大相对年化收益回撤比: 
    fall_value_list = [-0.67]
    rebound_rise_value_list = [0.07]
    rebound_fall_value_list = [-0.07]        
                                
    # 最小的相对最大回撤: 
    fall_value_list = [-0.79]
    rebound_rise_value_list = [0.19]
    rebound_fall_value_list = [-0.01]    

    return  fall_value_list, rebound_rise_value_list, rebound_fall_value_list    

def get_300_params():
    # 初始测试区间
    # fall_value_list = create_array(-1, -3, -79)
    # rebound_rise_value_list = create_array(1, 3, 29)
    # rebound_fall_value_list = create_array(-1, -3, -19)

    # 最大绝对年化收益值: 
    fall_value_list = [-0.40]
    rebound_rise_value_list = [0.07]
    rebound_fall_value_list = [-0.01]    

    # # 最大绝对年化收益回撤比:  
    # fall_value_list = [-0.76]
    # rebound_rise_value_list = [0.22]
    # rebound_fall_value_list = [-0.01]    

    # # 最小的绝对最大回撤:  
    # fall_value_list = [-0.79]
    # rebound_rise_value_list = [0.07]
    # rebound_fall_value_list = [-0.01]    

    # # 最大的相对收益: 
    # fall_value_list = [-0.46]
    # rebound_rise_value_list = [0.07]
    # rebound_fall_value_list = [-0.10]    

    # # 最大的相对收益回撤比: 
    # fall_value_list = [-0.73]
    # rebound_rise_value_list = [0.25]
    # rebound_fall_value_list = [-0.01]    

    # # 最小的相对最大回撤: 
    # fall_value_list = [-0.79]
    # rebound_rise_value_list = [0.07]
    # rebound_fall_value_list = [-0.01]    
                  
    # fall_value_list = [-0.73]
    # rebound_rise_value_list = [0.22]
    # rebound_fall_value_list = [-0.10]   

    return  fall_value_list, rebound_rise_value_list, rebound_fall_value_list

def get_800_params():
    # 初始测试区间
    # fall_value_list = create_array(-1, -3, -79)
    # rebound_rise_value_list = create_array(1, 3, 29)
    # rebound_fall_value_list = create_array(-1, -3, -19)

    # # 最大绝对年化收益值: 
    # fall_value_list = [-0.46]
    # rebound_rise_value_list = [0.10]
    # rebound_fall_value_list = [-0.01]    

    # # 最小的绝对最大回撤:  
    # fall_value_list = [-0.79]
    # rebound_rise_value_list = [0.07]
    # rebound_fall_value_list = [-0.01]    

    # # 最大绝对年化收益回撤比:  
    # fall_value_list = [-0.76]
    # rebound_rise_value_list = [0.25]
    # rebound_fall_value_list = [-0.01]    

    # 最大相对年化收益值: 
    # fall_value_list = [-0.46]
    # rebound_rise_value_list = [0.10]
    # rebound_fall_value_list = [-0.10]    

    # # 最小的相对最大回撤: 
    # fall_value_list = [-0.07]
    # rebound_rise_value_list = [0.01]
    # rebound_fall_value_list = [-0.19]   

    # 最大相对年化收益回撤比： 
    fall_value_list = [-0.43]
    rebound_rise_value_list = [0.01]
    rebound_fall_value_list = [-0.13]        
                  
    return  fall_value_list, rebound_rise_value_list, rebound_fall_value_list

def get_today_params():
    # 初始测试区间
    fall_value_list = create_array(-1, -3, -79)
    rebound_rise_value_list = create_array(1, 3, 29)
    rebound_fall_value_list = create_array(-1, -3, -19)

    # 最大绝对年化收益值: 
    fall_value_list = [-0.61]
    rebound_rise_value_list = [0.07]
    rebound_fall_value_list = [-0.04]    

    # 最小的绝对最大回撤:  
    fall_value_list = [-0.79]
    rebound_rise_value_list = [0.22]
    rebound_fall_value_list = [-0.01]    

    # 最大绝对年化收益回撤比:  
    fall_value_list = [-0.61]
    rebound_rise_value_list = [0.04]
    rebound_fall_value_list = [-0.04]    

    # 最大相对年化收益值:  
    fall_value_list = [-0.61]
    rebound_rise_value_list = [0.07]
    rebound_fall_value_list = [-0.04]    

    # 最小的相对最大回撤: 
    fall_value_list = [-0.49]
    rebound_rise_value_list = [0.01]
    rebound_fall_value_list = [-0.19]    

    # 最大相对年化收益回撤比: 
    fall_value_list = [-0.61]
    rebound_rise_value_list = [0.07]
    rebound_fall_value_list = [-0.04]                    


    # 最优参数
    # fall_value_list = [-0.03]
    # rebound_rise_value_list = [0.19]
    # rebound_fall_value_list = [-0.39] 

    # 当日涨跌幅，考虑涨跌停交易费用，参数趋势判断.
    # # A
    # fall_value_list = [-0.01, -0.02, -0.03, -0.04,-0.05,\
    #                     -0.06, -0.07, -0.08, -0.09]
    # rebound_rise_value_list = [0.01]
    # rebound_fall_value_list = [-0.39]        

    # # B
    # fall_value_list = [-0.03]                       
    # rebound_rise_value_list = [0.01, 0.03, 0.05, 0.07, 0.09,  \
    #                             0.11, 0.13, 0.15, 0.17, 0.19, \
    #                             0.21, 0.23, 0.25, 0.27, 0.29, \
    #                             0.31, 0.33, 0.35, 0.37, 0.39, \
    #                             0.41, 0.43, 0.45, 0.47, 0.49, \
    #                             0.51, 0.53, 0.55, 0.57, 0.59, \
    #                             0.61, 0.63, 0.65, 0.67, 0.69, \
    #                             0.71, 0.73, 0.75, 0.77, 0.79]
    # rebound_fall_value_list = [-0.39]   

    # # C
    # fall_value_list = [-0.03]                       
    # rebound_rise_value_list = [0.01]
    # rebound_fall_value_list = [-0.01, -0.03, -0.05, -0.07, -0.09,  \
    #                             -0.11, -0.13, -0.15, -0.17, -0.19, \
    #                             -0.21, -0.23, -0.25, -0.27, -0.29, \
    #                             -0.31, -0.33, -0.35, -0.37, -0.39]          


    # fall_value_list = [-0.09]
    # rebound_rise_value_list = [0.19]
    # rebound_fall_value_list = [-0.01]

    return  fall_value_list, rebound_rise_value_list, rebound_fall_value_list    

def get_today_improve_b():
    # 初始测试区间
    fall_value_list = create_array(-1, -3, -79)
    k1_list = create_array(-0.05, -0.2, -1)
    k2_list = create_array(0.05, 0.2, 1)
    k3_list = create_array(-1, -3, -19)

def get_test_params(trade_type):
    if trade_type == 'today_improve':
        return get_today_improve_params_20()
        # return get_300_params()
        # return get_today_improve_params_30()
        # return get_800_params()

    if trade_type == 'today':
        return get_today_params()

def test():
    dbhost = "localhost"
    data_type = 'MarketData_day'
    
    database_obj = get_database_obj(data_type)
    secode_list = database_obj.get_amarket_secode_list()

    # database_obj = MarketInfoDatabase(host=dbhost)
    # # index_code = '000300'
    # # index_code = '000906'
    # secode_list = database_obj.get_index_secode_list(index_code, 'tinysoft')

    # secode_list = ['SH600000']
    # secode_list = ['SH600000', 'SH600004']
    # secode_list = ['SH600000', 'SH600004', 'SH600006', 'SH600996']
    # trade_type = 'today_simple'
    trade_type = 'today_improve'
    # trade_type = 'today'
    data_start_date = 20100101
    data_end_date = 20180504 
    
    fall_value_list, rebound_rise_value_list, rebound_fall_value_list = get_test_params(trade_type)
    
    high_price_days_list = [20]
    for high_price_days in high_price_days_list:
        abc_obj = ABCCompute (dbhost, trade_type, \
                            data_type, high_price_days,\
                            data_start_date, data_end_date, 
                            secode_list, fall_value_list, \
                            rebound_rise_value_list,\
                            rebound_fall_value_list)
        # abc_obj.compute_main()
        abc_obj.compute_main_B()

def ana_sum_result():
    # file_name = 'D:/github/study/PyQt5/DownLoadData/ABC_Result'\
    #         + '/3511/today_improve/New_High_Days_20/sum_1890_3511.xlsx'

    file_name = 'D:/github/study/PyQt5/DownLoadData/ABC_Result'\
            + '/3511/today_improve/New_High_Days_30/sum_1890_3511.xlsx'

    # file_name = 'D:/github/study/PyQt5/DownLoadData/ABC_Result'\
    #         + '/300/today_improve/New_High_Days_20/sum_1890_300.xlsx'

    excelobj = EXCEL()
    data = excelobj.get_alldata_bysheet(file_name, 'sum_value')
    ab_max = 0.05
    ab_max_re = -0.15
    re_max_re = -0.10
    result = []
    row_index = 1
    # print (data[row_index])
    while row_index < len(data) - 6:
        if data[row_index][1] >= ab_max and data[row_index][2] > ab_max_re \
            and data[row_index][5] > re_max_re:
            result.append(data[row_index])
        row_index += 1

    print_list('result: ', result)

if __name__ == "__main__":
    test()
    # ana_sum_result()
