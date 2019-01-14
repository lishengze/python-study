from wind import Wind
from func_secode import *
from func_time import *

def get_wind_a_market_secode_list(code_type = "tinysoft"):
    wind_connect_obj = Wind()
    market_name = 'a001010100000000'
    market_secodelist = wind_connect_obj.get_market_secodelist(market_name)
    result = []
    for item in market_secodelist:
        result.append(get_complete_stock_code(item[0], code_type))
    return result

def get_wind_restore_data(wind_obj, date, code_name, time_type, end_date=''):
    start_date = date
    if end_date == '':
        end_date = start_date
    secode = trans_tinycode_to_wind(code_name)
    # secode = database_data[2]
    keyvalue_list = "close"

    if time_type == "day":
        # print("secode: %s, start_date: %s, end_date: %s" % \
        #         (secode, start_date, end_date))
        tmp = wind_obj.wind.wsd(secode, keyvalue_list, str(start_date), str(end_date), "PriceAdj=F")
    else:
        start_datetime = str(start_date) + " 09:00:00"
        end_datetime = str(end_date) + " 15:30:00"
        # minute_type = time_type[0:len(time_type)-1]
        time_str = "BarSize=%s" %(time_type)
        print("secode: %s, start_time: %s, end_time: %s, time_str: %s" % \
             (secode, start_datetime, end_datetime, time_str))

        tmp = wind_obj.wind.wsi(secode, keyvalue_list, str(start_datetime), str(end_datetime), time_str)
    if tmp.ErrorCode == 0:
        result = []
        # for i in range(len(tmp.Times)):
        #     result.append([])

        # for i in range(len(tmp.Times)):
        #     result[i].append(str(tmp.Times[i]))
        #     for j in range(len(keyvalue_list)):
        #         result[i].append(float("%.4f " % tmp.Data[j][i]))
        result = [start_date, code_name, float("%.8f " % tmp.Data[0][0]), 'wind']
        return result
        
        # print(result)
        # if len(result) > 0:
        #     return result[0][0]
        # else:
        #     return result
    else:
        raise(Exception("get_restore_historydata Failed , ErroCode is: %d" % (tmp.ErrorCode)))    