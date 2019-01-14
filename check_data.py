import time

import os, sys
import traceback
import pyodbc


import threading
import multiprocessing 

from CONFIG import *

from func_tool import *
from func_secode import *
from func_delist import *
from func_time import *
from func_connect import *
from func_data import *
from func_qt import update_tableinfo, update_tableinfo_with_rowdelta
from func_wind import *

from future_net import FutureNet
from future_database import FutureDatabase
from func_market import get_latest_contract_month
from tinysoft import TinySoft
from func_io import *
from func_frequency_data import *
from func_compute import *
import math

from wind import Wind
from excel import EXCEL
from datetime import datetime

def check_all_data(data_type_list=["MarketData_day", "MarketData_10m", "MarketData_15m", \
                                      "MarketData_30m", "MarketData_60m", "MarketData_120m"],  \
                      host="192.168.211.162", 
                      table_view=None, error_tableview = None):
    try:
        database_name   = "MarketData_day"
        database_obj    = get_database_obj(database_name, host=host)
        table_list      = database_obj.get_db_table_list()
        time_type       = get_time_type(database_name)
        wind_obj        = Wind()
        max_error       = 0.01
        ori_data_dict   = {}
        compare_dict    = {}
        index_code_list = get_index_code_list('tinysoft')
        log_file        = get_log_file(file_id='check_all')
        excel_obj       = EXCEL()

        for data_type in data_type_list:            
            table_list               = database_obj.get_db_table_list(data_type)
            time_type                = get_time_type(data_type)       
            ori_data_dict[time_type] = {}   
            # table_list               = ['SH600608', 'SZ002188', 'SZ002660', 'SZ000987','SH600193', \
            #                             'SZ000900', 'SH603600', 'SH600686', 'SH603368','SH603066',]
            data_numb = 1
            for code_name in table_list:            
                db_first_data = database_obj.get_first_day_data(code_name, data_type) 
                if len(db_first_data) == 0 or code_name in index_code_list:
                    # print(data_type, code_name)
                    table_list.remove(code_name)
                    continue 
                ori_data_dict[time_type][code_name] = [db_first_data[0], code_name, float(db_first_data[4]), time_type] 
                info = '%s, %s, %d' % (time_type, code_name, data_numb)
                log_info(log_file, info, table_view, error_tableview)
                data_numb += 1

            info = '获取 %s 最早数据完毕, 数据数目: %d \n' % (time_type, len(ori_data_dict[time_type]))
            log_info(log_file, info, table_view, error_tableview)

            # if 'day' == time_type:
            #     data_numb = 0
            #     ori_data_dict['wind'] = {}
            #     for code_name in ori_data_dict[time_type]:                 
            #         wind_data = get_wind_restore_data(wind_obj, ori_data_dict[time_type][code_name][0],\
            #                                           code_name, time_type)
            #         ori_data_dict['wind'][code_name] = wind_data
            #         info = 'wind %s, %d' % (code_name, data_numb)
            #         log_info(log_file, info, table_view, error_tableview)
            #         data_numb += 1                    

            #     info = '获取 wind 最早数据完毕, 数据数目: %d \n' % len(ori_data_dict['wind'])
            #     log_info(log_file, info, table_view, error_tableview)  

        for data_type in data_type_list:
            time_type = get_time_type(data_type)

            cmp_type = ''
            if time_type != "day":
                cmp_type  = '%s_day' % (time_type)
                compare_dict[cmp_type] = compare_restore_close(ori_data_dict[time_type], ori_data_dict['day'], max_error)

            # cmp_type  = '%s_wind' % (time_type)
            # compare_dict[cmp_type] = compare_restore_close(ori_data_dict[time_type], ori_data_dict['wind'], max_error)

            if cmp_type != '':
                info = '获取 %s 对比数据完毕, 数据数目: %d \n' % (cmp_type, len(compare_dict[cmp_type]))
                log_info(log_file, info, table_view, error_tableview) 

        time_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        check_file_name = '%s\Check\%s_check_all.xlsx' % (os.getcwd() , time_id)
        # check_file_name = os.getcwd()  + '\Check\check_tmp.xlsx'

        for data_type in compare_dict:
            info = '\ndata_type: %s, numb: %d' % (str(data_type), len(compare_dict[data_type]))
            log_info(log_file, info, table_view, error_tableview)
            excel_obj.write_all_data(compare_dict[data_type], check_file_name, str(data_type))
            for item in compare_dict[data_type]:
                log_info(log_file, str(item), table_view, error_tableview)

    except Exception as e:
        raise e

def get_detail_different_time(db_obj, wind_obj, code, time_type, start_date, log_file=None, max_error=0.001):
    database_name = 'MarketData_%s' % (time_type)
    if time_type != 'day':
        database_name += 'm'
    db_keyvalue_list = ['TDATE, TCLOSE']
    result = []

    db_latest_time = db_obj.get_latest_date(code, database_name)
    days_step = 365
    end_date = add_days(start_date, days_step)
    if int(end_date) > int(db_latest_time):
        end_date = db_latest_time

    db_close = 0
    wind_close = 0

    while int(start_date) <= int(db_latest_time):        
        delta = 100
        info = 'code: %s, start_date: %s, end_date: %s' % (code, start_date, end_date)
        log_info(log_file, info)

        db_data = db_obj.get_histdata_by_date(start_date, end_date, code, db_keyvalue_list, database_name)
        wind_data = wind_obj.get_histdata(code, ['close'], start_date, end_date, time_type)

        if len(db_data) != len(wind_data):
            info = 'code: %s, start_date: %s, end_date: %s db_data.size: %d, wind_data.size: %d' % \
                    (code, start_date, end_date, len(db_data), len(wind_data))
            log_info(log_file, info)
            return []

        for i in range(len(db_data)):
            db_close = float(db_data[i][1])
            wind_close = float(wind_data[i][1])
            delta = math.fabs((db_close-wind_close)/wind_close)
            if delta < max_error:
                result = [code, db_data[i][0], time_type, db_close, 'wind', wind_close, delta]
                return result
        
        start_date = add_days(end_date, 1)
        end_date = add_days(start_date, days_step)
        if int(end_date) > int(db_latest_time):
            end_date = db_latest_time
    
    if int(start_date) > int(db_latest_time):
        return ['ALL Error', code, db_latest_time, time_type, db_close, 'wind', wind_close]

def check_detail_data(table_view=None, error_tableview = None):
    excel_obj     = EXCEL()
    src_file_name = 'Check\\20181115_153347_check_all.xlsx'
    # src_file_name = 'Check\\test_check_detail.xlsx'
    des_file_id   = 'check_detail'
    des_file_name = '%s\Check\%s_%s.xlsx' % \
                    (os.getcwd() , datetime.now().strftime("%Y%m%d_%H%M%S"), des_file_id)    

    meta_info     = excel_obj.get_alldata_bysheet(src_file_name, 'all')
    db_obj        = MarketDatabase(host='192.168.211.162')
    wind_obj      = Wind()
    compare_dict  = {}
    log_file      = get_log_file(file_id=des_file_id)

    for data_type in meta_info:
        compare_dict[data_type] = []
        for item in meta_info[data_type]:
            code = item[0]
            time_type = item[1]
            date = str(int(item[2]))
            curr_result = get_detail_different_time(db_obj, wind_obj, code, time_type, date, log_file=log_file)
            compare_dict[data_type].append(curr_result)

    for data_type in compare_dict:
        log_info(log_file, str(data_type), table_view, error_tableview)
        excel_obj.write_all_data(compare_dict[data_type], des_file_name, str(data_type))
        for item in compare_dict[data_type]:
            log_info(log_file, str(item), table_view, error_tableview)
    
if __name__ == "__main__":
    check_all_data()
    # check_detail_data()