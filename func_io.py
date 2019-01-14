import os
import traceback
import datetime
from func_qt import *

def print_dict_data(msg, data):
    print('\n')
    print (msg, len(data))
    for item in data:
        print (item,": ", data[item])
    print('\n')

def print_list(msg, data, numb=50):
    print ('\n')
    print (msg, len(data))
    if len(data) > numb:
        data = data[0:numb]

    for item in data:
        print (item)

    print ('\n')

def print_data(data):
    if isinstance(data, dict):
        print('dict_data_numb: %d' % (len(data)))
        for item in data:
            print('item: %s' % (str(item)))
            print_data(data[item])        
    elif isinstance(data, list):    
        print('list_data_numb: %d' % (len(data)))    
        for item in data:
            print_data(item)        
    else:
        print(data, ' ')

def get_log_file(dir_name = 'Log', file_id = 'check_data', file_type='txt'):
    dir_name = os.getcwd() + '\\' + dir_name +'\\'
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except Exception as e:
            exception_info = str(traceback.format_exc())
            dir_exit_error = '文件已存在'
            if dir_exit_error not in exception_info:
                raise(e)
        
    log_file_name = dir_name + datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S") \
                    + '_' + file_id + '.'+ file_type
                    
    log_file = open(log_file_name, 'w+', encoding='utf-8')   
    return log_file

def log_info(log_file, info_str, table_view=None, error_tableview=None, exception_flag=False):
    print (info_str)
    if log_file != None:
        log_file.write(info_str + '\n')
    if True == exception_flag:
        update_tableinfo(error_tableview, info_str)
    else:
        update_tableinfo(table_view, info_str)

class TestIO(object):
    def __init__(self):
        self.__name__ = "TestIO"
        self.test_print_data()

    def test_print_data(self):
        data = {
            'name':  ['lee', 'James', 'Rose'],
            'age': [20, 25, 30]
        }
        print_data(data)

if __name__ == "__main__":
    testio_obj = TestIO()