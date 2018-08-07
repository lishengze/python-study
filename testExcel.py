from excel import EXCEL
import numpy as np
from func_tool import get_execl_code

# def test_get_secode():
#     dirname = "D:/strategy"
#     filename = "test.xlsx"
#     complete_filename = dirname + '/' + filename
#     excelobj = EXCEL(complete_filename)
#     # secodelist = excelobj.get_data_bysheet("test1")
#     secodelist = excelobj.get_data_byindex()

    # print secodelist

def get_data_secode():
    file_name = 'D:/github/study/PyQt5/DownLoadData/ABC_Result/800/today_improve/test.xlsx'
    excelobj = EXCEL()
    data = excelobj.get_alldata_bysheet(file_name)
    max_value_a = -10
    index_a = 0
    max_value_b = -10
    index_b = 0
    index = 0
    while index < len(data):
        item = data[index]
        if max_value_a < item[0] and item[0] != 0:
            max_value_a = item[0]
            index_a = index
        
        # if max_value_b < item[1] and item[1] != 0:
        #     max_value_b = item[1]
        #     index_b = index
        index += 1

    print('max_value_a: %f, index_a: %d, max_value_b: %f, index_b: %d' \
            % (max_value_a, index_a, max_value_b, index_b, ))

def test_xlwings():
    ori_data = np.empty([5,2],dtype=int)
    excelobj = EXCEL()
    file_name = 'D:/excel/test.xlsx'
    sheetname = 'test'
    excelobj.write_all_data(ori_data, file_name, sheetname=sheetname)
    # print(ori_data)
    # print(len(ori_data))
    # print(len(ori_data[0]))
    # print (ori_data[1][1])

def test_get_execl_code():
    file_name = 'D:/excel/2018成长分红.xlsx'
    secode_list = get_execl_code(file_name)
    print(secode_list)

if __name__ == "__main__":
    # get_data_secode()
    # test_xlwings()
    test_get_execl_code()


