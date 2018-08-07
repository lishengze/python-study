from download_marketdata import DowloadHistData
from func_time import *

def test_get_trans_data():
    data_type_list = ['MarketData_day']   
    # dbhost = "192.168.211.162"
    dbhost = "192.168.211.165"

    start_datetime = 20151101
    # end_datetime = getDateNow()    
    end_datetime = 20160201

    clear_database = 'False'
    source_conditions = [start_datetime, end_datetime]
    restore_dict = {}

    for data_type in data_type_list:
        download_obj = DowloadHistData(data_type=data_type, dbhost=dbhost, clear_database=clear_database, \
                                       table_view=None, error_tableview=None)  
        download_obj.store_transed_data(data_type, source_conditions, restore_dict)   

if __name__ == "__main__":
    test_get_trans_data()
