from wind import Wind
from func_secode import *

def get_a_market_secodelist(code_type = "tinysoft"):
    wind_connect_obj = Wind()
    market_name = 'a001010100000000'
    market_secodelist = wind_connect_obj.get_market_secodelist(market_name)
    result = []
    for item in market_secodelist:
        result.append(getCompleteSecode(item[0], code_type))
    return result