from func_time import *
from func_frequency_data import * 
from func_io import * 
from func_connect import *

import datetime

def test_transto_wind_datetime():
    intdate = 20180801
    str_date = transto_wind_datetime(intdate)
    print(str_date)

def test_datetime():
    curr_date = datetime.datetime.now()
    print(curr_date.isocalendar()[1])

def test_get_trade_start_time():
    curr_time = 141500
    delta_minute = get_trade_start_minute(141500)
    print("delta_minute: ", delta_minute)

def test_get_days_trans_data():
    database_name = "MarketData_day"
    dbhost = "192.168.211.162"
    database_obj = get_database_obj(database_name, dbhost)
    start_date = 20180801
    end_date = 20180806
    keyvalue_list = ['TDATE', 'TIME', 'TCLOSE']
    secode = "SH000300"
    ori_data = database_obj.get_histdata_by_date(start_date, end_date, secode, keyvalue_list, "MarketData_10m")
    print_list("ori_data: ", ori_data)

    # week_data = get_week_data(ori_data)
    # print_list("week_data: ", week_data)

    # month_data = get_month_data(ori_data)
    # print_list("month_data: ", month_data)

def test_get_minute_trans_data():
    database_name = "MarketData_10m"
    dbhost = "192.168.211.162"
    database_obj = get_database_obj(database_name, dbhost)
    start_date = 20180801
    end_date = 20180806
    keyvalue_list = ['TDATE', 'TIME', 'TCLOSE']
    secode = "SH000300"
    ori_data = database_obj.get_histdata_by_date(start_date, end_date, secode, keyvalue_list)

    minute_trans_data = get_minute_transed_data(ori_data, 60)
    print_list("minute_trans_data: ", minute_trans_data)    

if __name__ == "__main__":
    # test_transto_wind_datetime()
    # test_datetime()
    test_get_days_trans_data()
    # test_get_trade_start_time()
    # test_get_minute_trans_data()