import time
import traceback

from database import Database

from weight_database import WeightDatabase
from weight_datanet import WeightTinySoft

from market_database import MarketDatabase
from market_datanet import MarketTinySoft
from market_info_database import MarketInfoDatabase

from industry_database import IndustryDatabase
from industry_datanet import IndustryNetConnect

from market_realtime_database import MarketRealTimeDatabase
from market_info_database import MarketInfoDatabase

def get_database_obj(database_name, host='localhost', id=0):
    if "WeightData" in database_name:
        return WeightDatabase(host=host, db=database_name)

    if "MarketData" in database_name:
        return MarketDatabase(id=id, host=host, db=database_name)

    if "IndustryData" in database_name:
        return IndustryDatabase(host=host, db=database_name)

def get_netconn_obj(database_type, isReconnect=False):
    try:
        if True == isReconnect:
            info_str = "[T] Get_netconn_obj  Restart!"
            print(info_str)

        if "WeightData" in database_type:
            return WeightTinySoft(database_type)

        if "MarketData" in database_type:
            return MarketTinySoft(database_type) 

        if "IndustryData" in database_type:
            return IndustryNetConnect(database_type)    

    except Exception as e: 
        exception_info = "\n" + str(traceback.format_exc()) + '\n'
        info_str = "[E]: get_netconn_obj " + exception_info
        print(info_str)

        driver_error = "The driver did not supply an error"     
        connFailedError = "Communication link failure---InternalConnect"   
        connFailedWaitTime = 10
        if driver_error in info_str or connFailedError in info_str:
            print ("[T] Get_netconn_obj Sleep " + str(connFailedWaitTime) + "S")
            time.sleep(connFailedWaitTime)            
            get_netconn_obj(database_type, True)
        else:
            raise(Exception(exception_info))     