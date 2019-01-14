from excel import EXCEL
from CONFIG import *
from func_secode import *

def test_get_config_data():
    file_name = EXCEL_CONFIG_FILE_NAME
    excel_obj = EXCEL()
    sheet_name = 'index_list'
    # result = excel_obj.get_data_bysheet(file_name, sheet_name)
    result = excel_obj.get_onecolumn_data_by_sheet(file_name, sheet_name)
    print(result)

def trans_code():
    dir_name = 'D:/excel/'
    file_name = dir_name + "sector.xlsx"
    excel_obj = EXCEL()
    code_list = excel_obj.get_onecolumn_data_by_sheet(file_name)
    wind_code_list = []
    for code in code_list:
        wind_code_list.append(trans_tinycode_to_wind(code))

    desfile_name = dir_name + 'trans_sector.xlsx'
    excel_obj.write_single_column_data(wind_code_list, desfile_name)

if __name__ =="__main__":
    # test_get_config_data()
    trans_code()