import xlsxwriter

from market_database import MarketDatabase
from func_tool import get_secode_list_from_excel, getCompleteSecode
from operator import itemgetter, attrgetter
import time
import datetime
import threading 
import gc

class ExtractMarketData(object):
    def __init__(self, dbhost, data_type, start_date, end_date,\
                        ori_file_name, des_file_name, key_value_list):
        self.dbhost = dbhost
        self.data_type = data_type
        self.start_date = start_date
        self.end_date = end_date
        self.ori_file_name = ori_file_name
        self.des_file_name = des_file_name
        self.key_value_list = key_value_list
        self.work_thread_numb = 8
        self.lock = threading.Lock()
        self.completed_count = 0
        self.init_database()
        self.init_secode_list()
        self.init_excel_obj()

    def init_database(self):
        self.database = MarketDatabase(db=self.data_type, host=self.dbhost)
        self.database_list = []
        for i in range(self.work_thread_numb):
            tmp_database = MarketDatabase(db=self.data_type, host=self.dbhost)
            self.database_list.append(tmp_database)

    def init_secode_list(self):
        self.ori_secode_list = get_secode_list_from_excel(self.ori_file_name)
        # self.ori_secode_list = self.ori_secode_list[0:5*self.work_thread_numb]

    def init_excel_obj(self):
        self.excel_workbook = xlsxwriter.Workbook(self.des_file_name) 

    def set_curr_excel_sheet(self, sheetname):
        self.excel_worksheet = self.excel_workbook.get_worksheet_by_name(sheetname)
        if self.excel_worksheet is None:
            self.excel_worksheet = self.excel_workbook.add_worksheet(sheetname)

    def write_one_column(self, data, target_col, start_row=0):
        index = 0
        while index < len(data):            
            self.excel_worksheet.write(start_row+index, target_col, data[index])
            index += 1
        del data

    def write_one_row(self, data, target_row, start_col=0):
        index = 0
        while index < len(data):
            self.excel_worksheet.write(target_row, start_col+index, data[index])
            index += 1

    def save_file(self):
        self.excel_workbook.close()

    def set_time_data(self):
        index_code = 'SH000300'
        key_list = ["TDATE", "TIME"]
        ori_time_data = self.database.get_histdata_bytime(self.start_date, self.end_date, \
                                                        index_code, value_list=key_list)
        self.index_time_list = []
        self.string_time_list = []
        for item in ori_time_data:
            self.index_time_list.append([item[0], item[1]])
            self.string_time_list.append('%d %d' %(item[0], item[1]))

        self.string_time_list.insert(0, "time\\code")

    def complete_data(self, ori_result, index_time_list):
        unlist_data = []
        delist_data = []
        on_market = False
        curr_result_item = ori_result[0]

        result_time_list = []
        for item in ori_result:
            result_time_list.append([item[0], item[1]])

        for i in range(len(index_time_list)):
            item = index_time_list[i]
            if item not in result_time_list:
                if True == on_market:
                    # 停牌
                    ori_result.append([item[0], item[1], 0, curr_result_item[3]])
                    delist_data.append([item[0], item[1], 0, curr_result_item[3]])
                else:
                    # 未上市
                    ori_result.append([item[0], item[1], -1, -1])
                    unlist_data.append([item[0], item[1]])
            else:
                on_market = True
                curr_result_item = ori_result[result_time_list.index(item)]
        ori_result.sort(key=itemgetter(0,1))

        i = 0
        delete_data = []
        while i < len(ori_result):
            if [ori_result[i][0], ori_result[i][1]] not in index_time_list:
                delete_data.append(ori_result[i])
                ori_result.remove(ori_result[i])
                i = i - 1
            i = i + 1

        comp_data = []
        for item in ori_result:
            comp_data.append(item[2])
        return comp_data

    def read_data(self, secode, database_obj, keyvalue_list):
        ori_histdata = database_obj.get_histdata_bytime(self.start_date, self.end_date, \
                                                        table_name=getCompleteSecode(secode, "tinysoft"), \
                                                        value_list=keyvalue_list)
        comp_result = self.complete_data(ori_histdata, self.index_time_list)
        self.lock.acquire()
        comp_result.insert(0, secode)
        self.curr_result_list.append(comp_result)
        self.completed_count += 1
        print ('completed_count: %d' % (self.completed_count))
        self.lock.release()
        comp_result = None

    def start_read_thread(self, secode_list, keyvalue_list):
        print ('start_read_thread')
        thread_list = []
        self.curr_result_list = []
        index = 0
        while index < len(secode_list):
            tmp_thread = threading.Thread(target=self.read_data, \
                                        args=(secode_list[index], self.database_list[index], keyvalue_list,))            
            thread_list.append(tmp_thread)
            index += 1
            
        for thread in thread_list:
            thread.start()

        for thread in thread_list:
            thread.join()   

        for item in self.curr_result_list:
            self.write_one_column(item, self.column_index)
            self.column_index += 1

        self.curr_result_list = None
        gc.collect()
        # time.sleep(10)

    def write_main(self):
        self.set_time_data()                
        for key_value in self.key_value_list:
            self.set_curr_excel_sheet(key_value)
            self.column_index = 0
            self.write_one_column(self.string_time_list, self.column_index)
            self.column_index += 1
            curr_keyvalue_list = ["TDATE", "TIME", key_value]

            curr_secode_list = []         
            secode_index = 0               
            while secode_index < len(self.ori_secode_list):                
                secode = self.ori_secode_list[secode_index]
                curr_secode_list.append(secode)       

                if len(curr_secode_list) == self.work_thread_numb \
                    or secode_index == len(self.ori_secode_list) - 1:
                    self.start_read_thread(curr_secode_list, curr_keyvalue_list)
                    curr_secode_list = []
                secode_index += 1
                # print ('secode_index: %d, curr_secode_list.size: %d' \
                # % (secode_index, len(curr_secode_list)))

            gc.collect()
        self.save_file()    

    def write_single(self):
        self.set_time_data()                
        for key_value in self.key_value_list:
            self.set_curr_excel_sheet(key_value)
            self.column_index = 0
            self.write_one_column(self.string_time_list, self.column_index)
            self.column_index += 1
            curr_keyvalue_list = ["TDATE", "TIME", key_value]
  
            secode_index = 0               
            while secode_index < len(self.ori_secode_list):                
                secode = self.ori_secode_list[secode_index]
                ori_histdata = self.database.get_histdata_bytime(self.start_date, self.end_date, \
                                                                table_name=getCompleteSecode(secode, "tinysoft"), \
                                                                value_list=curr_keyvalue_list)
                comp_result = self.complete_data(ori_histdata, self.index_time_list)       
                self.write_one_column(comp_result, self.column_index)                  
                print('column_index: %d' %(self.column_index))
                self.column_index += 1
                del comp_result
                secode_index += 1

            gc.collect()
        self.save_file()    
def test():
    start_time = datetime.datetime.now()
    print ('----- Start At %s -----' % (start_time.strftime('%H:%M:%S')))
    dbhost = 'localhost'
    data_type = "MarketData_day"
    start_date = "20170130"
    end_date = "20180417"    
    ori_file_name = "D:\excel\沪深300成分股_Code.xlsx"
    des_file_name = "D:\excel\\test_1.xlsx"
    key_value_list = ['TCLOSE']
    extract_marketdata_obj = ExtractMarketData(dbhost, data_type, start_date, end_date, \
                                                ori_file_name, des_file_name, key_value_list)
    # extract_marketdata_obj.write_main()
    extract_marketdata_obj.write_single()

    end_time = datetime.datetime.now()
    cost_time = (end_time - start_time).total_seconds()
    print ('----- End At %s, Cost %d seconds -----' \
        % (start_time.strftime('%H:%M:%S'), cost_time))

if __name__ == '__main__':
    test()

                




