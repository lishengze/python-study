from func_connect import *
from func_data import *
from func_compute import *
from func_io import *
from excel import EXCEL
import datetime
import math


def get_typ_list(ori_data):
    result = []
    i = 0
    while i < len(ori_data):
        result.append((float(ori_data[i][0]) + float(ori_data[i][1])) / 2)
        i += 1
    return result

def compute_css_list(ori_typ_list, ave_numb=32, csst12_rate=0.014, csst_rate1=1.0/3.0, 
                    csst_rate2=2.0/3.0, max_css=300, min_css=-300, is_potential_energy=False):
    result    = []
    csst_list = []
    css_list  = []
    typ_list  = []

    for i in range(ave_numb):
        csst_list.append(0)
        css_list.append(0)
        result.append(0)
    result.append(0)

    for i in range(len(ori_typ_list)-1):
        typ_list.append((ori_typ_list[i] + ori_typ_list[i+1])/2)

    #print_list("trans_type_list: ", typ_list)
    i = ave_numb - 1
    while i < len(typ_list):
        typ_ave_value = get_ave(typ_list[i-ave_numb+1:i+1])
        csst11 = typ_list[i] - typ_ave_value;
        csst12 = csst12_rate * get_ave_dev(typ_list[i-ave_numb+1:i+1])
        csst13 = csst11 / csst12
        if i == ave_numb-1:
            csst = csst13;
        else:
            csst = csst_list[len(csst_list)-1] * csst_rate1 + csst13 * csst_rate2
        csst_list.append(csst)        

        css = rebound(csst, max_css, min_css)

        #if i < 100 and ave_numb == 84:
        #    print("index: %d, type_ave_value: %f, csst11: %f, csst12: %f, csst13: %f, csst: %f, css: %f\n" % \
        #            (i, typ_ave_value, csst11, csst12, csst13, csst, css) )

        css_list.append(css)
        i += 1

    if is_potential_energy == False:
        i = ave_numb
        while i < len(css_list) - 1:
            result.append((css_list[i] + css_list[i+1]) / 2)
            i += 1
    else:
        result = css_list
    
    return result
    

def compute_value(ori_data):
    result = 0
    typ_list = get_typ_list(ori_data)
    # print_list('typ_list', typ_list)
    css_list = compute_css_list(typ_list)
    energy_list = compute_css_list(typ_list, ave_numb=84, csst12_rate=0.014, csst_rate1=11.0/13.0, 
                                csst_rate2=2.0/13.0, max_css=300, min_css=-300, is_potential_energy=True)
    # print_list('css_list', css_list)
    result = [css_list[len(css_list)-1], energy_list[len(energy_list)-1]]
    return result

def get_curr_useful_date():
    curDate = datetime.datetime.now()
    curHourTime = float(datetime.datetime.now().strftime('%H'))
 
    new_date = curDate
    if curHourTime < 15:
        delta = datetime.timedelta(days=-1)
        new_date = curDate + delta
    result = new_date.strftime('%Y%m%d')
    return result    

def check_delistdata(ori_data):
    result = True
    today_datestr = get_curr_useful_date()
    if len(ori_data) == 0  \
    or str(ori_data[len(ori_data)-1][3]) != str(today_datestr):
        result = False
    return result

def compute_energy_data(dbhost='192.168.211.162', database_name="MarketData_60m"):
    db_obj     = get_database_obj(database_name, dbhost)
    table_list = db_obj.get_db_table_list()
    # table_list = ['SH000001']
    value_list = ['TCLOSE','TOPEN', 'SECODE', 'TDATE', 'TIME']
    result     = {}
    for table in table_list:
        db_data = db_obj.get_delist_histdata(table, value_list=value_list, data_numb=1000)
        if check_delistdata(db_data):
            date_str = db_data[len(db_data)-1][3]
            tmp_result =  compute_value(db_data)
            result[table] = [date_str, table, tmp_result[0], tmp_result[1]]
        else:
            print("delist code: %s \n" %(table))

    time_type = database_name.split('_')[1]
    write_data(result, time_type)

def write_data(comp_result, time_type):
    trans_data = []
    for code_name in comp_result:
        trans_data.append(comp_result[code_name])

    # print(trans_data)
    dir_name  = "//192.168.211.182/it程序设计/主指标计算/"
    # dir_name  = "D:/excel/"
    file_name = "%s%s_%s_主指标.xlsx" % (dir_name, datetime.datetime.now().strftime("%Y_%m_%d"), time_type)
    excel_obj = EXCEL()
    excel_obj.write_all_data(trans_data, file_name)

class TestComputeEnergyData(object):
    def __init__(self):
        self.__name__ = 'TestComputeEnergyData'
        self.test_compute()

    def test_compute(self):
        dbhost = '192.168.211.162'
        database_name = "MarketData_60m"
        compute_energy_data(dbhost, database_name)

if __name__ == '__main__':
    test_obj = TestComputeEnergyData()