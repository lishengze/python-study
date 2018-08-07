# 提供计算前复权数据的功能；
from func_time import *

def get_day_transed_data(ori_data, time_type):
    if time_type == "week":
        return get_week_data(ori_data)

    if time_type == "month":
        return get_month_data(ori_data)
    
def get_week_data(ori_day_data):
    result = []
    start_index = 0
    while start_index < len(ori_day_data):
        cur_date = getDate(int(ori_day_data[start_index][0]))
        next_date = cur_date + datetime.timedelta(1)
        if isTradingDay(next_date) == False:            
            result.append(ori_day_data[start_index])
        start_index += 1    
    return result

def get_month_data(ori_day_data):
    result = []
    start_index = 0
    while start_index < len(ori_day_data):
        cur_date = getDate(int(ori_day_data[start_index][0]))
        next_trading_day = get_next_trading_day(cur_date)
        if next_trading_day.month != cur_date.month:
            result.append(ori_day_data[start_index])
        start_index += 1
    return result

def get_minute_transed_data(ori_minute_data, time_type):
    result = []
    for item in ori_minute_data:
        cur_time = item[1]
        start_time = get_trade_start_minute(cur_time)
        if start_time % time_type == 0:
            result.append(item)
    return result


