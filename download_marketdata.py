import time

import os, sys
import traceback
import pyodbc

import datetime
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
from energy_compute import *
import math

from wind import Wind

class DowloadHistData(object):
    def __init__(self, data_type, dbhost, clear_database, thread_count = 8, \
                table_view=None, error_tableview = None):
        self.dbhost = dbhost
        self.clear_database = clear_database
        self.thread_count = thread_count
        self.table_view = table_view
        self.error_tableview = error_tableview
        self.write_com_count = 0
        self.write_sucess_count_lock = threading.Lock()
        self.data_type = data_type
        self.process_datanumb_once = 200000
        self.wind_obj = Wind()
        self.day_trans_dict ={
            "week": "MarketData_week",
            "month": "MarketData_month"
        }                  
        self.init_log()

    def init_log(self):
        self.log_write_lock = threading.Lock()
        dir_name = os.getcwd() + '\Log\\'
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name)
            except Exception as e:
                exception_info = str(traceback.format_exc())
                dir_exit_error = '文件已存在'
                if dir_exit_error not in exception_info:
                    raise(e)
            
        self.log_file_name = dir_name + datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S") \
                           + '_' +self.data_type +'.txt'
        self.log_file = open(self.log_file_name, 'w+', encoding='utf-8')

    def log_info(self, info_str, exception_flag = False):
        self.log_write_lock.acquire()
        print (info_str)
        self.log_file.write(info_str + '\n')
        if True == exception_flag:
            update_tableinfo(self.error_tableview, info_str)
        else:
            update_tableinfo(self.table_view, info_str)
        self.log_write_lock.release()

    def log_restore_info_dict(self, restore_info_dict):
        info_str = '\n前复权信息 \n'
        restore_info_dict = pure_dict_data(restore_info_dict)
        if len(restore_info_dict) > 0:
            self.log_info(info_str)
        
        numb = 0
        for secode in restore_info_dict:
            if len(restore_info_dict[secode]) != 0:
                info_str = '%s: 复权时间: %d %d, 复权数据数目: %d' % \
                            (secode, restore_info_dict[secode][0], restore_info_dict[secode][1], \
                            restore_info_dict[secode][2])
                self.log_info(info_str)  
                numb += 1

        if len(restore_info_dict) > 0:
            info_str = '\n前复权股票数为: %d' % (numb)
            self.log_info(info_str)        

    def get_write_success_count(self):
        self.write_sucess_count_lock.acquire()
        self.write_com_count += 1
        self.write_sucess_count_lock.release()
        return self.write_com_count

    def reset_write_success_count(self):
        self.write_sucess_count_lock.acquire()
        self.write_com_count = 0
        self.write_sucess_count_lock.release()        

    def get_start_end_date(self, oridata):
        start_date = oridata[0][0]
        end_date = oridata[len(oridata)-1][0]
        return start_date, end_date

    def write_daydata_transed_data(self, result_array, table_name, database_obj):
        for item in self.day_trans_dict:
            transed_data = get_day_transed_data(result_array, item)
            start_date,end_date = self.get_start_end_date(transed_data)
            database_obj.delete_data_by_date(start_date, end_date, table_name, self.day_trans_dict[item])
            for data in transed_data:
                database_obj.insert_data(data, table_name, self.day_trans_dict[item])

        curr_write_sucess_count = self.get_write_success_count()
        info_str = '[I]%d, %s: 写入数据: %d, 数据类型: %s \n' % \
                    (curr_write_sucess_count, table_name, len(transed_data), item)

        self.log_info(info_str)  

    def write_data_to_database(self, result_array, source, database_obj, isRestart=False, database_name=""):
        try:
            if True == isRestart:
                info_str = "[RS]: %s, %s, 重启写入数据, 数据库ID: %d, 线程ID: %s" % \
                            (database_name, source, database_obj.id, str(threading.currentThread().getName()))
                self.log_info(info_str)

            table_name = source 
            if database_name == "":
                database_name = database_obj.db
                                           
            duplicate_insert_numb = 0
            if self.clear_database == True:            
                database_obj.insert_multi_data(result_array, table_name, database_name)   
            else:
                for item in result_array:
                    try:
                        database_obj.insert_data(item, table_name, database_name)
                    except Exception as e:
                        exception_info = "\n" + str(traceback.format_exc()) + '\n'
                        duplicate_insert_error = "Violation of PRIMARY KEY constraint"
                        if duplicate_insert_error in exception_info:
                            if "WeightData" not in database_name:
                                duplicate_insert_numb += 1          
                                database_obj.update_data(item, table_name, database_name)
                        else:
                            break
                            exception_info  = "插入当前数据失败，停止当前线程工作，具体异常信息为: " + exception_info
                            self.log_info(exception_info, True) 
                            raise(Exception(exception_info))

            curr_write_sucess_count = self.get_write_success_count()
            if "MarketData" in database_name and len(result_array) > 0:
                start_date,end_date = self.get_start_end_date(result_array)
                info_str = '[I] %d, %s, %s, [%d, %d]: 写入数据: %d, DP数据: %d \n' % \
                            (curr_write_sucess_count, database_name, source, start_date, end_date, \
                            len(result_array) - duplicate_insert_numb, duplicate_insert_numb)
            else:           
                info_str = '[I] %d, %s, %s: 写入数据: %d, DP数据: %d \n' % \
                            (curr_write_sucess_count, database_name, source, \
                            len(result_array) - duplicate_insert_numb, duplicate_insert_numb)

            self.log_info(info_str)        
        except Exception as e:
            sleeptime = 1000
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            info_str = '[X] %s, %s 写入数据库失败, %d 秒后重新写入数据' % (database_name, source, sleeptime)
            self.log_info(info_str)  
            
            info_str = "详细异常信息为: %s" % (exception_info)
            self.log_info(info_str, True)  

            time.sleep(sleeptime)
            self.write_data_to_database(result_array, source, database_obj, True, database_name)

    def init_write_net_data_thread(self, netdata_array, source_array, database_obj_list):
        threads = []
        for i in range(len(netdata_array)):
            tmp_thread = threading.Thread(target=self.write_data_to_database, 
                                          args=(netdata_array[i], str(source_array[i]), database_obj_list[i],))
            threads.append(tmp_thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()      

    def init_write_trans_data_thread(self, trans_data_list, table_list, database_obj_list):
        threads = [] 
        index = 0
        for i in range(len(table_list)):
            for data_type in self.day_trans_dict: 
                tmp_thread = threading.Thread(target=self.write_data_to_database, 
                                                args=(trans_data_list[i][data_type], str(table_list[i]), \
                                                    database_obj_list[index], False, self.day_trans_dict[data_type],))
                # print_list(data_type, trans_data_list[i][data_type])
                threads.append(tmp_thread)
                index += 1

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()      

    def is_left_intervel_bg(self, ori_netdata, latest_data):
        result = True
        if len(latest_data) > 0 and len(ori_netdata) > 0:
            net_max_time = [ori_netdata[len(ori_netdata)-1][0], ori_netdata[len(ori_netdata)-1][1]]
            latest_time = [latest_data[0], latest_data[1]]
            result = is_time_late(net_max_time, latest_time)
        if len(latest_data) > 0 and len(ori_netdata) == 0:
            result = False
        return result

    def is_left_intervel(self, curr_condition):
        result = True
        if curr_condition[3] == 'right':
            result = False
        return result        

    def get_database_obj_list(self, database_name, max_thread_count=100):
        database_obj_list = []
        if self.thread_count > max_thread_count:
            self.thread_count = max_thread_count

        for i in range(self.thread_count):
            tmp_database_obj = get_database_obj(database_name, host=self.dbhost, id=i+1)
            database_obj_list.append(tmp_database_obj)   
        return database_obj_list     

    def store_market_data(self, database_name, source_conditions):
        try:
            source_conditions.append(self.clear_database)
            starttime            = datetime.datetime.now()
            pro_start_time_str   = starttime.strftime("%Y-%m-%d %H:%M:%S")
            code_type            = source_conditions[2]
            info_str             = ('%s, %s, 开始时间: %s \n' % (database_name, code_type, pro_start_time_str))
            database_obj         = get_database_obj(database_name, host=self.dbhost)
            netconn_obj          = get_netconn_obj(database_name)
            source               = netconn_obj.get_sourceinfo(source_conditions)
            table_name_list      = netconn_obj.get_tablename(source_conditions)            
            database_obj_list    = self.get_database_obj_list(database_name, len(table_name_list))
            ori_start_time       = source_conditions[0]
            ori_end_time         = source_conditions[1]

            self.write_com_count = 0            
            curr_datanumb        = 0
            tmp_netdata_array    = []
            tmp_tablename_array  = []       
            delist_info_dict     = get_empty_dict(table_name_list, [])
            restore_info_dict    = get_empty_dict(table_name_list, [])

            if code_type == "stock":
                com_tradetime_list = get_index_tradetime(netconn_obj, ori_start_time, ori_end_time)

            if 'True' == self.clear_database or True == self.clear_database:
                info_str += ("** 清空 %s 数据库 ** \n" % (database_name))
                database_obj.clearDatabase(table_name_list)
            database_obj.completeDatabaseTable(table_name_list)  

            info_str += ("数据源数量 : %d \n" % len(table_name_list))
            self.log_info(info_str)

            for table_index in range(len(table_name_list)):        
                cur_tablename        = table_name_list[table_index]
                cur_source           = netconn_obj.get_cursource(cur_tablename, source) 
                cur_first_data       = database_obj.getFirstData(cur_tablename)                        
                cur_latest_data      = database_obj.getLatestData(cur_tablename)   
                dbtransed_conds_list = database_obj.get_transed_conditions(cur_tablename, cur_source)                                    
                cur_netdata          = []

                if len(dbtransed_conds_list) == 0:
                    info_str = '[D] %d, %s, 已有数据\n' % (table_index+1, str(cur_source))
                    self.log_info(info_str)
                    continue

                condition_index = len(dbtransed_conds_list) - 1        
                while condition_index >= 0:
                    cur_condition  = dbtransed_conds_list[condition_index]
                    ori_netdata    = netconn_obj.get_netdata(cur_condition)
                    isLeftInterval = False  
                    start_datetime = cur_condition[1]
                    end_datetime   = cur_condition[2]

                    if ori_netdata is None:
                        info_str = '[C] %s: %s 无数据' % (cur_tablename, str(cur_condition))
                        self.log_info(info_str) 
                        ori_netdata = []
                    else:          
                        info_str = '[B] %d, %s, %s, 原始数据: %d, '% (table_index+1, database_name, \
                                                                str(cur_condition), len(ori_netdata))

                        if code_type == 'stock':    
                            # Complete delist Data
                            isLeftInterval   = self.is_left_intervel(cur_condition)
                            old_oridata_numb = len(ori_netdata)
                            tradetime_array  = get_sub_index_tradetime(com_tradetime_list, start_datetime, end_datetime)
                            ori_netdata      = com_delist_data(tradetime_array, ori_netdata, isLeftInterval, cur_latest_data)
                            delist_datanumb  = len(ori_netdata) - old_oridata_numb

                            # Restore Data
                            ori_netdata, restore_info = get_restore_data(database_obj, cur_tablename, ori_netdata, \
                                                                         isLeftInterval, cur_first_data)

                            if isLeftInterval == False and restore_info != []:                       
                                cur_first_data = ori_netdata[0]                                                                    
                            if isLeftInterval == True and restore_info_dict[cur_tablename] != [] and restore_info != []:
                                restore_info_dict[cur_tablename][2] += restore_info[2]
                            elif restore_info_dict[cur_tablename] == []:
                                restore_info_dict[cur_tablename] = restore_info
                            delist_info_dict[cur_tablename] = delist_datanumb

                            info_str += "停牌数据: %d, 前复权:%s  \n" % ((delist_datanumb), str(restore_info))
                        else:
                            info_str += "\n"
                            
                        self.log_info(info_str)
                    condition_index -= 1
                    ori_netdata.extend(cur_netdata)
                    cur_netdata = deep_copy_list(ori_netdata)
                    ori_netdata = []

                curr_datanumb += len(cur_netdata)
                tmp_netdata_array.append(cur_netdata)
                tmp_tablename_array.append(cur_tablename)            

                if len(tmp_netdata_array) % self.thread_count == 0 \
                or table_index == len(table_name_list) - 1 \
                or curr_datanumb >= self.process_datanumb_once:
                    self.init_write_net_data_thread(tmp_netdata_array, tmp_tablename_array, database_obj_list)
                    tmp_netdata_array   = []
                    tmp_tablename_array = []      
                    curr_datanumb       = 0   
                        
            self.log_restore_info_dict(restore_info_dict)
            
            endtime = datetime.datetime.now()
            costTime = (endtime - starttime).seconds
            info_str = "%s 结束时间: %s, 耗费: %.2fm\n" % \
                        (database_name, endtime.strftime("%Y-%m-%d %H:%M:%S"), costTime/60)
            self.log_info(info_str)

            if database_name == "MarketData_60m" and "stock" in source_conditions[2]:
                compute_energy_data(dbhost=self.dbhost, database_name=database_name)

            # if database_name == "MarketData_day" and "stock" in source_conditions[2]:
            #     ori_time = [source_conditions[0], source_conditions[1]]
            #     self.store_transed_data(database_name, ori_time, restore_info_dict)
        except Exception as e:
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            info_str = "__Main__ Failed" + "[E] Exception : \n" + exception_info
            self.log_info(info_str, True)

            connFailedError = "Communication link failure---InternalConnect"
            driver_error = "The driver did not supply an error"
            tiny_error = "self.curs.execute(tsl_str)"
            sql_error = "self.cur.execute(sql)"
            connFailedWaitTime = 30
            if connFailedError in info_str \
            or driver_error in info_str \
            or tiny_error in info_str \
            or sql_error in info_str:
                info_str = "[RS] self.store_net_data restart after %d S " % (connFailedWaitTime)
                self.log_info(info_str, True)
                time.sleep(connFailedWaitTime)
                info_str = "\n[RS] self.store_net_data  Restart : \n"
                self.log_info(info_str, True)
            else:
                info_str = "插入历史数据出现无解错误请退出, 详细信息为: %s" % (exception_info)
                self.log_info(info_str, True)
    
    def store_weight_data(self, data_type, source_conditions):
        pass

    def store_industry_data(self, data_type, source_conditions):
        pass

    def store_net_data(self, data_type, source_conditions):
        try:
            starttime = datetime.datetime.now()
            if len(source_conditions) > 2:
                info_str = '%s, %s, 开始时间: %s ' % \
                            (data_type, source_conditions[2], starttime.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                info_str = '%s, 开始时间: %s ' % \
                            (data_type, starttime.strftime("%Y-%m-%d %H:%M:%S"))  

            self.log_info(info_str)
            self.write_com_count = 0
            source_conditions.append(self.clear_database)

            database_name = data_type
            database_obj = get_database_obj(database_name, host=self.dbhost)

            netconn_obj = get_netconn_obj(data_type)
            source = netconn_obj.get_sourceinfo(source_conditions)
            table_name_list = netconn_obj.get_tablename(source_conditions)

            if 'True' == self.clear_database or True == self.clear_database:
                self.log_info("** 清空 %s 数据库 **" % (data_type))
                database_obj.clearDatabase(table_name_list)

            source = database_obj.filter_source(source)
            table_name_list = database_obj.filter_tableArray(table_name_list)
            info_str = "数据源数量 : " + str(len(table_name_list)) + '\n'
            self.log_info(info_str)

            database_obj.completeDatabaseTable(table_name_list)
            
            database_obj_list = self.get_database_obj_list(database_name)

            tmp_netdata_array = []
            tmp_tablename_array = []
            indexcode_list = get_index_code_list('tinysoft')

            delist_info_dict = {}
            restore_info_dict = {}
            curr_datanumb = 0
            
            if "MarketData" in data_type:
                com_tradetime_list = get_index_tradetime(netconn_obj, source_conditions[0], source_conditions[1])
                for table_name in table_name_list:
                    restore_info_dict[table_name] = []
                    delist_info_dict[table_name] = []

            table_index = 0
            while table_index < len(table_name_list):        
                cur_tablename = table_name_list[table_index]
                cur_source = netconn_obj.get_cursource(cur_tablename, source)                        
                cur_netdata = []
                if "MarketData" in data_type:
                    cur_first_data = database_obj.getFirstData(cur_tablename)                        
                    cur_latest_data = database_obj.getLatestData(cur_tablename)

                dbtransed_conds_list = database_obj.get_transed_conditions(cur_tablename, cur_source)
                if len(dbtransed_conds_list) == 0:
                    info_str = '[D] %d, %s, 已有数据\n' % (table_index+1, str(cur_source))
                    self.log_info(info_str)
                    table_index += 1
                    continue

                condition_index = len(dbtransed_conds_list) - 1        
                while condition_index >= 0:
                    cur_condition = dbtransed_conds_list[condition_index]
                    ori_netdata = netconn_obj.get_netdata(cur_condition)
                    isLeftInterval = False

                    if 'Industry' not in data_type:
                        start_datetime = cur_condition[1]
                        end_datetime = cur_condition[2]     

                    if ori_netdata is None:
                        if 'Industry' not in data_type:
                            info_str = '[C] %s: [%d, %d] 无数据' % (cur_tablename, start_datetime, end_datetime)
                        else:
                            info_str = '[C] %s: %s 无数据' % (cur_tablename, str(cur_condition))

                        self.log_info(info_str) 
                        ori_netdata = []
                    else:          
                        if 'Industry' not in data_type:          
                            info_str = '[B] %d, %s, [%d, %d] 原始数据: %d, ' % \
                                    (table_index+1, cur_tablename, start_datetime, end_datetime, len(ori_netdata))
                        else:
                            info_str = '[B] %d, %s, %s 原始数据: %d, ' % \
                                    (table_index+1, cur_tablename, str(cur_condition), len(ori_netdata))

                        if "MarketData" in data_type and cur_tablename not in indexcode_list:    
                            # Complete delist Data
                            isLeftInterval = self.is_left_intervel(cur_condition)
                            old_oridata_numb = len(ori_netdata)
                            try:
                                tradetime_array = get_sub_index_tradetime(com_tradetime_list, start_datetime, end_datetime)
                                ori_netdata = com_delist_data(tradetime_array, ori_netdata, isLeftInterval, cur_latest_data)
                            except Exception as e:
                                print ('cur_tablename: %s, isLeftInterval: %s' % (cur_tablename, isLeftInterval))
                                print (ori_netdata)
                                print (start_datetime, end_datetime)
                                raise(e)

                            info_str += "停牌数据: %d, " % (len(ori_netdata) - old_oridata_numb)
                            delist_info_dict[cur_tablename] = len(ori_netdata) - old_oridata_numb

                            # Restore Data
                            ori_netdata, restore_info = get_restore_data(database_obj, cur_tablename, ori_netdata, \
                                                                        isLeftInterval, cur_first_data)

                            if isLeftInterval == False and restore_info != []:                       
                                cur_first_data = ori_netdata[0]                                        
                            
                            if isLeftInterval == True and restore_info_dict[cur_tablename] != [] and restore_info != []:
                                restore_info_dict[cur_tablename][2] += restore_info[2]
                            elif restore_info_dict[cur_tablename] == []:
                                restore_info_dict[cur_tablename] = restore_info
                            
                            info_str += "前复权:%s \n" % (str(restore_info))
                        else:
                            info_str += "\n"
                            
                        self.log_info(info_str)
                    condition_index -= 1
                    cur_netdata.extend(ori_netdata)
                    # print('cur_netdata.size: %d' % len(cur_netdata))

                curr_datanumb += len(cur_netdata)
                tmp_netdata_array.append(cur_netdata)
                tmp_tablename_array.append(cur_tablename)            

                if len(tmp_netdata_array) % self.thread_count == 0 or table_index == len(table_name_list) - 1 \
                    or curr_datanumb >= self.process_datanumb_once:
                    self.init_write_net_data_thread(tmp_netdata_array, tmp_tablename_array, database_obj_list)
                    tmp_netdata_array = []
                    tmp_tablename_array = []      
                    curr_datanumb = 0           
                table_index += 1

            self.log_restore_info_dict(restore_info_dict)
            
            endtime = datetime.datetime.now()
            costTime = (endtime - starttime).seconds
            info_str = "%s 结束时间: %s, 耗费: %.2fm\n" % \
                        (data_type, endtime.strftime("%Y-%m-%d %H:%M:%S"), costTime/60)
            self.log_info(info_str)

            # if data_type == "MarketData_day" and "stock" in source_conditions[2]:
            #     ori_time = [source_conditions[0], source_conditions[1]]
            #     self.store_transed_data(data_type, ori_time, restore_info_dict)

        except Exception as e:
            exception_info = "\n" + str(traceback.format_exc()) + '\n'
            info_str = "__Main__ Failed" + "[E] Exception : \n" + exception_info
            self.log_info(info_str, True)

            connFailedError = "Communication link failure---InternalConnect"
            driver_error = "The driver did not supply an error"
            tiny_error = "self.curs.execute(tsl_str)"
            sql_error = "self.cur.execute(sql)"
            connFailedWaitTime = 30
            if connFailedError in info_str \
            or driver_error in info_str \
            or tiny_error in info_str \
            or sql_error in info_str:
                info_str = "[RS] self.store_net_data restart after %d S " % (connFailedWaitTime)
                self.log_info(info_str, True)
                time.sleep(connFailedWaitTime)
                info_str = "\n[RS] self.store_net_data  Restart : \n"
                self.log_info(info_str, True)
            else:
                info_str = "插入历史数据出现无解错误请退出, 详细信息为: %s" % (exception_info)
                self.log_info(info_str, True)
      
    def store_transed_data(self, data_type, ori_time, restore_info_dict):
        starttime = datetime.datetime.now()
        info_str = '周频 月频 开始更新时间: %s ' % \
                    (starttime.strftime("%Y-%m-%d %H:%M:%S"))   
        self.log_info(info_str)     
        self.reset_write_success_count()

        database_obj_list = self.get_database_obj_list(data_type)
        database_obj = get_database_obj(data_type, host=self.dbhost)

        if 'True' == self.clear_database or True == self.clear_database:            
            for curr_data_type in self.day_trans_dict:
                self.log_info("** 清空 %s 数据库 **" % (self.day_trans_dict[curr_data_type]))
                database_obj.clearDatabase(database_name=self.day_trans_dict[curr_data_type])

        table_list = database_obj.get_db_table_list()
        # print(table_list)
        for data_type in self.day_trans_dict:            
            database_obj.completeDatabaseTable(table_list, self.day_trans_dict[data_type])

        write_data_numb = 0
        write_data_list = []
        curr_table_list = []
        index = 0
        while index < len(table_list):
            table_name = table_list[index]
            comp_time = self.get_com_trans_time(table_name, database_obj, ori_time, restore_info_dict)
            if len(comp_time) < 2:
                # print(table_name, ori_time)
                error_info = '%s, %s 无法正确转换' % (table_name, str(ori_time))
                self.log_info(error_info, False)
            else:
                try:
                    ori_database_data = database_obj.get_histdata_by_date(comp_time[0],comp_time[1], table_name)
                except Exception as e:
                     exception_info = str(traceback.format_exc())
                     if "Invalid column" in exception_info:
                         excep_info = 'invalid column %s, %s, %s' % (str(comp_time[0]), str(comp_time[1]), table_name)
                         self.log_info(excep_info, False)

                # ori_database_data = database_obj.get_histdata_by_date(comp_time[0],comp_time[1], table_name)
                trans_data = self.get_trans_day_data(ori_database_data)

                write_data_list.append(trans_data)
                curr_table_list.append(table_name)
                write_data_numb += len(trans_data)

                if write_data_numb == self.thread_count or index == len(table_list)-1 or \
                    write_data_numb + len(self.day_trans_dict) > self.thread_count:
                    self.init_write_trans_data_thread(write_data_list, curr_table_list, database_obj_list)
                    write_data_numb = 0
                    write_data_list = []
                    curr_table_list = []
            index+=1
            
        endtime = datetime.datetime.now()
        costTime = (endtime - starttime).seconds
        info_str = "周频, 月频 更新结束时间: %s, 耗费: %.2fm\n" % \
                    (endtime.strftime("%Y-%m-%d %H:%M:%S"), costTime/60)
        self.log_info(info_str)

    def get_trans_day_data(self, ori_database_data):
        result = {}
        for data_type in self.day_trans_dict:
            trans_data = get_day_transed_data(ori_database_data, data_type)
            # print_list(data_type, trans_data)
            result[data_type] = trans_data
        return result
                
    def get_com_trans_time(self, table_name, database_obj, ori_time, restore_info_dict):
        comp_time = []
        for trans_type in self.day_trans_dict:
            database_name = self.day_trans_dict[trans_type]
            transed_conditions = database_obj.get_transed_conditions(table_name, ori_time, database_name)
            # print('table_name: ', table_name, 'ori_time: ', ori_time, 'transed_conditions: ', transed_conditions)
            if len(transed_conditions) == 2:
                transed_time = [transed_conditions[0][1], transed_conditions[1][2]]
            elif len(transed_conditions) == 1:
                transed_time = [transed_conditions[0][1], transed_conditions[0][2]]
            else:
                break
            # print("transed_time: ", transed_time)
            if table_name in restore_info_dict and len(restore_info_dict[table_name]) != 0:
                transed_time[0] = database_obj.get_first_date(table_name)[0][0]
                # print('dbNanme: ', self.data_type, 'table_name: ', table_name, 'transed_time: ', transed_time)
            comp_time = self.get_trans_time(comp_time, transed_time)
        return comp_time

    def get_trans_time(self, ori_time_list, new_time_list):
        result = []
        if len(ori_time_list) == 0:
            result.append(new_time_list[0])
            result.append(new_time_list[1])
        else:
            start_time = min(ori_time_list[0], new_time_list[0])
            end_time = max(ori_time_list[1], new_time_list[1])
            result.append(start_time)
            result.append(end_time)
        return result

def download_histdata(dbhost, data_type_list, source_conditions, clear_database, \
                           table_view=None, error_tableview = None):
    if 'WeightData' in data_type_list:
        download_index_secodeList(dbhost, table_view)
        download_market_secodeList(dbhost, table_view)
        update_future_contract(dbhost, table_view)

    if "MarketData" in data_type_list[0]:
        update_index_data(dbhost=dbhost, source_conditions=source_conditions,data_type_list=data_type_list, \
                          clear_database=clear_database, table_view=table_view, error_tableview=error_tableview)

    for data_type in data_type_list:
        print(dbhost, data_type, source_conditions, clear_database)
        download_obj = DowloadHistData(data_type=data_type, dbhost=dbhost, clear_database=clear_database, \
                                       table_view=table_view, error_tableview = error_tableview)  
        
        if "MarketData" in data_type:
            download_obj.store_market_data(data_type, source_conditions)
        else:
            download_obj.store_net_data(data_type, source_conditions)      

def download_histdata_main(dbhost, data_type_list, source_conditions, clear_database, \
                           table_view=None, error_tableview = None):  

    print(dbhost, data_type_list, source_conditions, clear_database)

    download_histdata(dbhost, data_type_list, source_conditions, 
                      clear_database, table_view, error_tableview)

    if wait_today_histdata_time(table_view, data_type_list[0]):
        source_conditions[1] = getDateNow()
        download_histdata(dbhost, data_type_list, source_conditions, 
                      clear_database, table_view, error_tableview)

    wait_nexttradingday_histdata_time(table_view, data_type_list[0])
    source_conditions[1] = getDateNow()
    download_histdata_main(dbhost, data_type_list, source_conditions, \
                            clear_database, table_view, error_tableview)
            
def update_future_contract(dbhost='localhost', table_view = None):
    starttime = datetime.datetime.now()
    info_str = '%s  开始更新沪深300合约表 ' %  (starttime.strftime("%Y-%m-%d %H:%M:%S"))
    update_tableinfo(table_view, info_str)
    print(info_str)

    index_code = '000300'
    future_net_obj = FutureNet()
    IF_contract_list = future_net_obj.get_contract_list(index_code)
    print_list('IF_contract_list: ', IF_contract_list)

    future_database_obj = FutureDatabase(host=dbhost)    
    future_database_obj.refreshDatabase([index_code])
    future_database_obj.insert_multi_data(IF_contract_list, index_code)

    endtime = datetime.datetime.now()
    info_str = '%s  更新沪深300合约表结束 ' %  (endtime.strftime("%Y-%m-%d %H:%M:%S"))
    update_tableinfo(table_view, info_str)
    print(info_str)    

def download_info_data():
    # data_type_list = ["IndustryData"]
    # data_type_list = [ "WeightData"]
    data_type_list = ["IndustryData", "WeightData"]
    # host = "localhost"
    dbhost = "192.168.211.162"  # win10
    start_datetime = 20180101
    end_datetime = getDateNow()

    download_histdata_main(dbhost = dbhost, data_type_list = data_type_list, \
                           source_conditions = [start_datetime, end_datetime],\
                           clear_database = False)
        
def download_index_secodeList(dbhost, table_view = None):
    indexcode_list = get_index_code_list('tinysoft')

    starttime = datetime.datetime.now()
    info_str = '%s  开始更新指数成分数据表 ' %  (starttime.strftime("%Y-%m-%d %H:%M:%S"))
    update_tableinfo(table_view, info_str)
    print(info_str)

    database_obj = MarketInfoDatabase(host=dbhost)

    for indexcode in indexcode_list:
        tableName = indexcode + "_SecodeList"        
        date = datetime.datetime.now().strftime("%Y%m%d")

        connect_obj = WeightTinySoft("")
        result = connect_obj.get_secode_list_info(indexcode, date)

        info_str = ""
        if result != None:
            info_str += '%s secode numb: %d' % (indexcode, len(result))
            database_obj.refreshSecodeListTable(tableName)
            database_obj.insertSecodeList(result, tableName)
        else:
            info_str += '%s has no secode' % (indexcode)

        update_tableinfo(table_view, info_str)
        print(info_str)

    endtime = datetime.datetime.now()
    info_str = '%s  更新指数成分数据表结束 ' %  (endtime.strftime("%Y-%m-%d %H:%M:%S"))
    update_tableinfo(table_view, info_str)
    print(info_str)

def download_market_secodeList(dbhost, table_view = None):
    starttime = datetime.datetime.now()
    info_str = '%s  开始更新板块成分数据表 ' %  (starttime.strftime("%Y-%m-%d %H:%M:%S"))
    update_tableinfo(table_view, info_str)
    print(info_str)    
    
    database_obj = MarketInfoDatabase(host=dbhost)    
    connect_type = "wind"

    if connect_type == "tinysoft":
        tiny_connect_obj = TinySoft()
        marketinfo_dict = {
            'A股':    "A_Market",
            '上证A股': "A_Market_SH",
            '深证A股': "A_Market_SZ",
            '创业板':  "A_Market_GEM",
            '中小企业板':  "A_Market_SME"
        }

        for market_name in marketinfo_dict:
            market_secodelist = tiny_connect_obj.get_market_secodelist(market_name)
            database_obj.insertSecodeList(market_secodelist, marketinfo_dict[market_name])
            info_str = '%s secode numb: %d' % (market_name, len(market_secodelist))
            update_tableinfo(table_view, info_str)
            print(info_str)
    
    if connect_type == "wind":
        wind_connect_obj = Wind()
        marketinfo_dict = {
            'a001010100000000': ["A_Market", "A 股市场"],
            'a001010200000000': ["A_Market_SH", "上证 A股"],
            'a001010300000000': ["A_Market_SZ", "深证A股"],
            'a001010500000000': ["A_Market_SZ_Main", "深圳主板A股"],
            'a001010r00000000': ["A_Market_GEM", "创业板"],
            'a001010400000000': ["A_Market_SME", "中小企业板"],
            '1000009396000000': ["A_Market_SME_With_ST", "中小企业板(含ST)"]
        }

        # marketinfo_dict = {
        #     'a001010100000000': "A_Market"
        # }        
        for market_name in marketinfo_dict:
            market_secodelist = wind_connect_obj.get_market_secodelist(market_name)
            database_obj.insertSecodeList(market_secodelist, marketinfo_dict[market_name][0])
            info_str = '%s secode numb: %d' % (marketinfo_dict[market_name][1], len(market_secodelist))
            update_tableinfo(table_view, info_str)
            print(info_str)

    endtime = datetime.datetime.now()
    info_str = '%s  更新板块成分数据表结束 ' %  (endtime.strftime("%Y-%m-%d %H:%M:%S"))
    update_tableinfo(table_view, info_str)
    print(info_str)      

def trans_marketd_data():
    data_type = 'MarketData_day'                     
    # dbhost = "192.168.211.162"
    dbhost = "192.168.211.165"

    start_datetime = 20170825
    end_datetime = getDateNow()
    clear_database = False
    source_conditions = [start_datetime, end_datetime]

    download_obj = DowloadHistData(data_type=data_type, dbhost=dbhost, clear_database=clear_database, \
                                    table_view=None, error_tableview=None)  
    download_obj.store_transed_data(data_type, source_conditions, {})   

def download_Marketdata():
    # data_type_list = ['IndustryData']  
    # data_type_list = ['MarketData_15m', 'MarketData_30m', \
    #                   'MarketData_60m', 'MarketData_120m']
    data_type_list = ['MarketData_day']                   
    # dbhost = "192.168.211.162"
    dbhost = "192.168.211.165"

    start_datetime = 20180101
    # end_datetime = 20180101
    end_datetime = getDateNow()
    clear_database = False
    
    source_conditions = [start_datetime, end_datetime, 'stock']
    for data_type in data_type_list:
        download_obj = DowloadHistData(data_type=data_type, dbhost=dbhost, clear_database=clear_database, \
                                       table_view=None, error_tableview=None)     
        download_obj.store_market_data(data_type, source_conditions)    

def update_index_data(dbhost='localhost', source_conditions=[], data_type_list = [], clear_database='False', \
                        table_view=None, error_tableview=None):    
    new_source_conditions = copy_array(source_conditions)
    new_source_conditions[2] = 'index'

    # data_type_list = ['MarketData_5m', 'MarketData_10m', \
    #                   'MarketData_15m', 'MarketData_30m', \
    #                   'MarketData_60m', 'MarketData_120m', \
    #                   'MarketData_day', 'MarketData_week', \
    #                   'MarketData_month']   

    if data_type_list == []:
        data_type_list = ['MarketData_10m', 'MarketData_15m', \
                        'MarketData_30m', 'MarketData_60m', \
                        'MarketData_120m', 'MarketData_day']   

    # data_type_list = ['MarketData_day'] 

    for data_type in data_type_list:
        download_obj = DowloadHistData(data_type=data_type, dbhost=dbhost, clear_database=clear_database, \
                                       table_view=table_view, error_tableview=error_tableview)  
        # download_obj.store_net_data(data_type, new_source_conditions)   
        download_obj.store_market_data(data_type, new_source_conditions)    
        
def download_index_data():
    start_datetime = 20050101
    end_datetime = getDateNow()
    dbhost = "192.168.211.165"
    clear_database = False
    source_conditions = [start_datetime, end_datetime, 'index']
    update_index_data(dbhost, source_conditions, clear_database)

def store_database_tablename(host, database_name):
    database_obj = get_database_obj(database_name, host)
    table_name_list = database_obj.get_db_table_list()
    marketinfo_database_obj = MarketInfoDatabase(host=host)  
    marketinfo_database_obj.insert_dbinfo(database_name, table_name_list)

def update_database_tablename_list():
    dbhost = "192.168.211.162"
    database_name_list = ["MarketData_day", "MarketData_10m", "MarketData_15m", \
                          "MarketData_30m", "MarketData_60m", "MarketData_120m", \
                          "MarketData_week", "MarketData_month"]
    for database_name in database_name_list:
        store_database_tablename(dbhost, database_name)

if __name__ == "__main__":
    # download_index_data()
    # download_Marketdata()
    # update_database_tablename_list();
    download_index_secodeList(dbhost = "192.168.211.162")
    # download_market_secodeList(dbhost = "192.168.211.162")
    # update_future_contract(dbhost='192.168.211.162')
    # update_future_contract()
    # download_Marketdata()
    # trans_marketd_data()
    # download_info_data()