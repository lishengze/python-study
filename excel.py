import xlrd

class EXCEL(object):
    def __init__(self, filename):
        self.__name__ = "EXCEL"
        self.excel =  xlrd.open_workbook(filename)

    def get_data_bysheet(self, sheetname = u'Sheet1'):
        table = self.excel.sheet_by_name(sheetname)
        secode_list = []
        for i in range(table.nrows):
            secode_list.append(str(int(table.cell(i,0).value)))
        return secode_list

    def get_data_byindex(self, index = 0):
        table = self.excel.sheet_by_index(index)
        secode_list = []
        for i in range(table.nrows):
            secode_list.append(str(int(table.cell(i,0).value)))
        return secode_list
