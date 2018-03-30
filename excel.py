import xlrd
import xlwt
import xlutils
from xlutils.copy import copy
import xlsxwriter
import openpyxl
import os

class EXCEL(object):
    def __init__(self):
        self.__name__ = "EXCEL"        
        self.workbook = xlwt.Workbook()

    def get_data_bysheet(self, filename, sheetname = u'Sheet1'):
        self.readHandle =  xlrd.open_workbook(filename)
        table = self.readHandle.sheet_by_name(sheetname)
        secode_list = []
        for i in range(table.nrows):
            secode_list.append(str(table.cell(i,0).value))
        return secode_list

    def get_data_byindex(self, filename, index = 0):
        self.readHandle =  xlrd.open_workbook(filename)
        table = self.readHandle.sheet_by_index(index)
        secode_list = []
        for i in range(table.nrows):
            secode_list.append(str(int(table.cell(i,0).value)))
        return secode_list

    def write_data(self, oridata, file_name, sheetname = u"Sheet1"):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheetname, cell_overwrite_ok=False)

        for i in range(len(oridata)):
            for j in range(len(oridata[i])):
                sheet.write(i, j, oridata[i][j])
        workbook.save(file_name)

    def init_xlwt(file_name):
        self.readbook = xlrd.open_workbook(file_name)        
        self.workbook = copy(readbook)

    def save_xlwt(file_name):
        self.workbook.save(file_name)

    def write_single_column_data_xlwt(self, oridata, file_name, col=0, sheetname = u"Sheet1"):
        readbook = xlrd.open_workbook(file_name)        
        workbook = copy(readbook)
        sheet_namelist = readbook.sheet_names()
        if sheetname not in sheet_namelist:
            worksheet = workbook.add_sheet(sheetname, cell_overwrite_ok=True)
        else:            
            worksheet = workbook.get_sheet(sheetname)

        for i in range(len(oridata)):
                worksheet.write(i, col, oridata[i])

        workbook.save(file_name)        

    def write_all_data_xlwt(self, oridata, file_name, sheetname = "Sheet1"):
        if sheetname not in self.readbook.sheet_names():
            worksheet = self.workbook.add_sheet(sheetname, cell_overwrite_ok=True)
        else:            
            worksheet = self.workbook.get_sheet(sheetname)

        for i in range(len(oridata)):
            for j in range(len(oridata[i])):
                worksheet.write(i, j, oridata[i])

    def write_single_column_data_xlsxwriter(self, oridata, file_name, col=0, sheetname = "Sheet1"):
        workbook = xlsxwriter.Workbook(file_name)        
        print len(workbook.worksheets())
        worksheet = workbook.get_worksheet_by_name(sheetname)
        
        if worksheet is None:
            print 'add worksheet'
            worksheet = workbook.add_worksheet(sheetname)

        print worksheet

        for i in range(len(oridata)):
            print i, col, oridata[i]
            worksheet.write(i, col, oridata[i])

        workbook.close()   

    def write_single_column_data_openpyxl(self, oridata, file_name, col=0, sheetname = "Sheet1"):
        if os.path.exists(file_name):
            workbook = openpyxl.load_workbook(file_name)
        else:
            workbook = openpyxl.Workbook()
            for cur_sheetname in workbook.sheetnames:
                workbook.remove(workbook[cur_sheetname])

        if sheetname not in workbook.sheetnames:
            print 'creat worksheet: ', sheetname
            worksheet = workbook.create_sheet(sheetname)
        else:
            worksheet = workbook[sheetname]    

        for i in range(len(oridata)):
            worksheet.cell(row=i+1, column=col+1, value=oridata[i])

        workbook.save(file_name) 

    def write_all_data_openpyxl(self, oridata, file_name, sheetname = "Sheet1"):
        if os.path.exists(file_name):
            workbook = openpyxl.load_workbook(file_name)
        else:
            workbook = openpyxl.Workbook()
            for cur_sheetname in workbook.sheetnames:
                workbook.remove(workbook[cur_sheetname])

        if sheetname not in workbook.sheetnames:
            print 'creat worksheet: ', sheetname
            worksheet = workbook.create_sheet(sheetname)
        else:
            worksheet = workbook[sheetname]    

        print "\n----- Start Write data To ", sheetname, " -----"
        for i in range(len(oridata)):
            for j in range(len(oridata[i])):
                worksheet.cell(row=j+1, column=i+2, value=oridata[i][j])
            print "i: ", i+1, ", secode: ", oridata[i][0], ", numb: ", len(oridata[i])

        workbook.save(file_name) 

    def write_single_column_data(self, oridata, file_name, col=0, sheetname = "Sheet1"):
        self.write_single_column_data_openpyxl(oridata, file_name, col, sheetname)

    def write_all_data(self, oridata, file_name, sheetname = "Sheet1"):
        self.write_all_data_openpyxl(oridata, file_name, sheetname)
        # self.write_all_data_xlwt(oridata, file_name, sheetname)
