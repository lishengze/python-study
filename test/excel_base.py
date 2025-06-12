import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
from datetime import datetime
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side, colors
from openpyxl.styles import numbers
from openpyxl.chart import BarChart, Reference, Series
from openpyxl.drawing.image import Image
from matplotlib.ticker import FixedLocator, FixedFormatter
from matplotlib.ticker import PercentFormatter
from matplotlib.ticker import ScalarFormatter
import xlrd
import sys
import json
import os
import logging
import math

import matplotlib.pyplot as plt
import matplotlib
import re
import numpy as np

logging.basicConfig(level = logging.INFO,  format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s', 
                    filename='运行日志.log',
                    filemode='w')
plt.rcParams['font.family'] = 'sans-serif' 
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

x_label_count = 6

g_test_pic = False

def get_test_data():
    np.random.seed(0)
    date_rng = pd.date_range(start='2025-03-15', end='2025-04-01', freq='D')
    strategy_net_value = np.cumprod(1 + 0.001 * np.random.randn(len(date_rng)))  # 模拟策略净值
    # strategy_net_value[0] = 1.2
    resut ={
        'date': date_rng.strftime('%Y-%m-%d').tolist(),
        'unit_net_value': strategy_net_value.tolist()
    }
    return resut, strategy_net_value[len(strategy_net_value)-1]
    # drawdown = -0.01 * np.random.randn(len(date_rng))  # 模拟回撤    

def get_config():
    try:
        config_file = open('配置.json', 'r', encoding='utf-8')
        config = json.load(config_file)
    except FileNotFoundError:
        logging.info("配置文件未找到，请检查路径。")
        return None
    except json.JSONDecodeError:
        logging.info("配置文件格式错误，请检查格式。")
        return None
    return config

def set_sheet_middle(sheet):
    try:
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal='center', vertical='center')
    except Exception as e:
        logging.error(f"设置单元格居中时发生错误: {e}")  
             

def set_value(sheet, row, col, key, value, file_name, is_number = False, border = None):
    try:
        if key in value:
            if is_number:
                sheet.cell(row = row, column = col, value = float(value[key])).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            else:
                sheet.cell(row = row, column = col, value = value[key])
                
            if border is not None:
                sheet.cell(row = row, column = col).border = border
        else:
            logging.warning(f"字段 {key} 不存在于文件{file_name}中。")
            
    except Exception as e:
        logging.error(f"设置{file_name} 单元格 {key} 值时发生错误: {e}")  
             
def get_last_row(sheet, sheet_name, col=1):
    try:
        valid_row = -2
        for i in range(sheet.max_row):
            if sheet.cell(row=i+1, column=col).value is not None:
                valid_row = i
        if valid_row == -2:
            logging.critical(f"文件 {sheet_name} 中未找到有效行，请检查。")
            
    except Exception as e:
        logging.error(f"读取sheet {sheet_name} 最后一行净值 时发生错误: {e}")  
            
    return valid_row + 1                
    
def get_last_jz(sheet, sheet_name):
    try:
        valid_row = get_last_row(sheet, sheet_name)
            
        last_jz = float(sheet.cell(row=valid_row, column=2).value)
    except Exception as e:
        logging.error(f"读取sheet {sheet_name} 最后一行净值 时发生错误: {e}")  
            
    return last_jz

def get_row(sheet,sheet_name,col, value_type='float'):
    result = []
    try:

        valid_row = get_last_row(sheet, sheet_name, col)
        
        for i in range(2, valid_row+1):

            if value_type == 'float':
                tmp = str(sheet.cell(row=i, column=col).value)
                if tmp.find('%') >= 0:
                    
                    new_s = tmp.replace('%', '')
                    result.append(float(new_s)/100)

                    # logging.info(f"{tmp}, {new_s}, {float(new_s)/100}")
                else:   
                    result.append(float(tmp))
            else:
                result.append(sheet.cell(row=i, column=col).value)
            
    except Exception as e:
        logging.error(f"读取sheet {sheet_name} 第 {col} 列时发生错误: {e}")  
            
    return result      

def get_all_jz_info(sheet, sheet_name):
    jz_dict = {
        "date":[],
        "unit_net_value":[]
    }    
    try:

        valid_row = get_last_row(sheet, sheet_name)
        
        for i in range(2, valid_row+1):
            date = str(sheet.cell(row=i, column=1).value)
            unit_net_value = float(sheet.cell(row=i, column=2).value)
            jz_dict["date"].append(date)
            jz_dict["unit_net_value"].append(unit_net_value)
            
    except Exception as e:
        logging.error(f"读取sheet {sheet_name} 最后一行净值 时发生错误: {e}")  
            
    return jz_dict                
    


def calc_hc_rate(unit_net_value):
    '''
    计算回撤数据
    '''
    try:
        if len(unit_net_value) < 2:
            return [0]
        else:
            result = []
            for i in range(1, len(unit_net_value)):
                result.append((unit_net_value[i] - unit_net_value[i-1]) / unit_net_value[i-1])
            return result
    except Exception as e:
        logging.error(f"计算回撤数据 时发生错误: {e}")

    return []

def calc_max_drawdown(unit_net_value, hc_list):
    '''
    计算最大回撤
    '''
    try:
        max_value = unit_net_value[0]
        for i in range(0, len(unit_net_value)):
            if unit_net_value[i] > max_value:
                max_value = unit_net_value[i]
            
        tmp_value = min(0,(unit_net_value[len(unit_net_value)-1] - max_value) / max_value)
        hc_list.append(tmp_value)
        return hc_list   
    except Exception as e:
        logging.error(f"计算最大回撤 时发生错误: {e}")  
    return []

def get_resize_index(date_list, target_count):
    '''
    计算缩放索引
    '''
    try:
        index_list = []

        if len(date_list) < target_count:   
            for i in range(len(date_list)):
                index_list.append(i)        
            return index_list, date_list
        else:
            step = int(len(date_list) / target_count)
            result = []
            for i in range(0, len(date_list), step):
                result.append(date_list[i])
                index_list.append(i)
            return index_list, result
    except Exception as e:
        logging.error(f"计算缩放索引 时发生错误: {e}")  
    return [], []

class FutureStaticStruct:
    def __init__(self):            
        self.mckc_ = {}
        self.mrpc_ = {}
        self.mrkc_ = {}
        self.mcpc_ = {}
        self.kc_ = {} # 空仓
        self.dc_ = {} # 多仓
        self.qlc_ = {} # 权利仓
        self.ywc_ = {} # 义乌仓
        self.amount_ = 0
        self.count_ = 0

    def get_trade_info(self, type_name, index):
        try:
            info = f'{index},{type_name}:'
            has_data = False
            if len(self.mckc_) > 0 or len(self.mrpc_) > 0 or len(self.mrkc_) > 0 or len(self.mcpc_) > 0:
                has_data = True
                info += '\n'
            if len(self.mckc_) > 0:
                info += f'卖出开仓: {len(self.mckc_)}只 ('
                for key, value in self.mckc_.items():
                    info += f'{key},'          
                info = info[:len(info)-1]
                info += ')\n'    
            if len(self.mrpc_) > 0:
                info += f'买入平仓: {len(self.mrpc_)}只 ('
                for key, value in self.mrpc_.items():
                    info += f'{key},'
                info = info[:len(info)-1]
                info += ')\n'                    
            if len(self.mrkc_) > 0:
                info += f'买入开仓: {len(self.mrkc_)}只 ('
                for key, value in self.mrkc_.items():
                    info += f'{key},'
                info = info[:len(info)-1]
                info += ')\n'
            if len(self.mcpc_) > 0:
                info += f'卖出平仓: {len(self.mcpc_)}只 ('
                for key, value in self.mcpc_.items():
                    info += f'{key},'
                info = info[:len(info)-1]
                info += ')\n'
            if has_data == False:
                info += f'无\n'
            return info
        except Exception as e:
            logging.error(f"读取{type_name} 单元格 {index} 值时发生错误: {e}")  
        return ''
   
            
    def get_hold_info(self, type_name):
        try:
            info = f'{type_name} {len(self.kc_) + len(self.dc_) + len(self.qlc_) + len(self.ywc_)}只 ('
            has_data = False
            if len(self.kc_) > 0 or len(self.dc_) > 0 or len(self.qlc_) > 0 or len(self.ywc_) > 0:
                has_data = True
            if len(self.kc_) > 0:
                info += f'空仓: {len(self.kc_)}只,'
            if len(self.dc_) > 0:
                info += f'多仓: {len(self.dc_)}只,'
            if len(self.qlc_) > 0:
                info += f'权利仓: {len(self.qlc_)}只,'
            if len(self.ywc_) > 0:
                info += f'义务仓: {len(self.ywc_)}只,'                                    
            info = info[:len(info)-1]
            if has_data == True:
                info += ')'    
            info += '\n'       
            return info        
        except Exception as e:
            logging.error(f"读取{type_name} 单元格 值时发生错误: {e}")
        return ''    

                                   
def get_future_type_name(code):
    """根据期货代码判断品种类型"""
    code = code.upper()  # 统一转换为大写
    if code.startswith(('TS', 'TF', 'T','TL')):
        return '国债期货'
    elif code.startswith('AU'):
        return '黄金期货'
    elif code.startswith('CU'):
        return '铜期货'
    else:
        return '其他品种'    

class ExcelDataRead():
    def __init__(self):
        pass
    
    def read_excel_sheet(self, xlrd_sheet, data_type, sheet_type='量化一'): 
        try:
            if data_type == '单元资产':
                return self.read_dyzc_data(self=self , xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)
            elif data_type == '汇总证券-合计':
                return self.read_hzzq_hj(self=self , xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)   
            elif data_type == '交易所回购':
                return self.read_jyshg(self=self, xlrd_sheet=xlrd_sheet,sheet_type=sheet_type)   
            elif data_type == '期货保证金分析':
                return self.read_qhbzjfx(self=self, xlrd_sheet=xlrd_sheet,sheet_type=sheet_type) 
            elif data_type == '成交回报':
                return self.read_cjhb(self=self, xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)    
            elif data_type == '汇总证券-当日持仓':
                return self.read_hzzq_drcc(self=self, xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)  
            elif data_type == '汇总证券-合计-股票':
                return self.read_hzzz_hj_gp(self=self, xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)                                          
            else:
                return True
        except Exception as e:
            logging.error(f"读取文件 {data_type} 时发生错误: {e}")  
        return False   
    
    def read_dyzc_data(self, xlrd_sheet, sheet_type="量化一"):
        try:
            cell_dict = {}
            header = []
            logging.info(f"读取文件 单元资产 开始 {xlrd_sheet.nrows} {xlrd_sheet.ncols} ")
            for col in range(xlrd_sheet.ncols):
                # ori_data[col] = []
                is_cell_name = False
                for row in range(xlrd_sheet.nrows):
                    # logging.info(f"单元格 {row} {col}")
                    cell_value = str(xlrd_sheet.cell_value(row, col))
                    
                    if is_cell_name:
                        if row == xlrd_sheet.nrows - 1:
                            cell_value = '合计'
                        cell_dict[cell_value] = {
                            "row": row
                        }
                                            
                    if '资产单元名称' in cell_value:
                        is_cell_name = True            
                        
            # 将投机单元放置在权益单元前面;
            tmp_tj_cell_list = []
            tmp_qy_cell_list = []
            
            for key, value in cell_dict.items():
                if '投机' in key:
                    tmp_tj_cell_list.append(key)
                elif '权益' in key:
                    tmp_qy_cell_list.append(key)
            
            tmp_cell_dict = {}
            for cell in tmp_tj_cell_list:
                tmp_cell_dict[cell] = cell_dict[cell]
            
            for cell in tmp_qy_cell_list:
                tmp_cell_dict[cell] = cell_dict[cell]
                
            cell_dict = tmp_cell_dict
            
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                header.append(cell_value)
            
            # print(header)
                        
            for key, value in cell_dict.items():
                nrow = value['row']
                for col in range(xlrd_sheet.ncols):
                    cell_value = str(xlrd_sheet.cell_value(nrow, col))
                    cell_dict[key][header[col]] = cell_value

            # print(cell_dict) 
            return cell_dict
        except Exception as e:
            logging.error(f"读取文件 单元资产 时发生错误: {e}")  
            
        return None   
        
    def read_hzzq_hj(self, xlrd_sheet, sheet_type="量化一"):
        try:
            cell_dict = {}
            logging.info(f"读取文件 汇总证券-合计 开始 {xlrd_sheet.nrows} {xlrd_sheet.ncols} ")
            target_col = xlrd_sheet.ncols - 1            
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                if '总体盈亏(含费用)' in cell_value:
                    target_col = col
                        
            print('target_col', target_col)
            cell_value = str(xlrd_sheet.cell_value(xlrd_sheet.nrows - 1, target_col))
            profit = float(cell_value)
            profit = round(profit, 4)
            cell_dict['profit'] = profit
            
            # print(cell_dict)
            return cell_dict
        except Exception as e:
            logging.error(f"读取文件 汇总证券-合计 时发生错误: {e}")  
            
        return None                          

    def read_jyshg(self, xlrd_sheet, sheet_type="量化一"):
        try:
            profit_col = -1
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                if '利润' == cell_value:
                    profit_col = col
                    
            if profit_col == -1:
                logging.critical("文件中未找到利润列，请检查。")
                
                            
            cell_dict = {}
            logging.info(f"读取文件 交易所回购 开始 {xlrd_sheet.nrows} {xlrd_sheet.ncols} ")
            for row in range(xlrd_sheet.nrows):
                for col in range(xlrd_sheet.ncols):
                    cell_value = str(xlrd_sheet.cell_value(row, col))
                    if row == xlrd_sheet.nrows - 1 and col == profit_col:
                        profit = float(cell_value)
                        profit = round(profit, 4)
            cell_dict['profit'] = profit
            return cell_dict
        except Exception as e:
            logging.error(f"读取文件 交易所回购 时发生错误: {e}")  
            
        return None     
            
    def read_qhbzjfx(self, xlrd_sheet, sheet_type="量化一"):
        try:
            cell_dict = {}
            header = []
            logging.info(f"读取文件 单元资产 开始 {xlrd_sheet.nrows} {xlrd_sheet.ncols} ")
            for col in range(xlrd_sheet.ncols):
                # ori_data[col] = []
                is_cell_name = False
                for row in range(xlrd_sheet.nrows):
                    if row == xlrd_sheet.nrows - 1:
                        break
                    cell_value = str(xlrd_sheet.cell_value(row, col))
                    
                    if is_cell_name:
                        if row == xlrd_sheet.nrows - 1:
                            cell_value = '合计'
                        cell_dict[cell_value] = {
                            "row": row
                        }
                                            
                    if '资产单元名称' in cell_value:
                        is_cell_name = True
            
            
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                header.append(cell_value)
            
            # print(header)
                        
            for key, value in cell_dict.items():
                nrow = value['row']
                for col in range(xlrd_sheet.ncols):
                    cell_value = str(xlrd_sheet.cell_value(nrow, col))
                    if header[col] == '占用保证金(静态)' or header[col] == '账户权益' or header[col] == '风险比例1(%)':
                        cell_dict[key][header[col]] = round(float(cell_value), 4)

            # print(cell_dict)        
            return cell_dict

        except Exception as e:
            logging.error(f"读取文件 期货保证金 时发生错误: {e}")  
            
        return None     

    def read_cjhb_lhs(self, xlrd_sheet):
        try:
            cell_dict = {}            
            header_col_dict = {}
            result_dict = {}
            
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                valid_item = ['成交数量', '成交金额', '证券代码', '委托方向', '证券类别']                
                if cell_value in valid_item:
                    header_col_dict[cell_value] = col
                    cell_dict[cell_value] = []
                           
            for key, col in header_col_dict.items():
                for nrow in range(xlrd_sheet.nrows):
                    if nrow == 0 or nrow == xlrd_sheet.nrows - 1:
                        continue
                    cell_value = str(xlrd_sheet.cell_value(nrow, col))    
                    # print(cell_value)                
                    if key == '成交数量' or key == '成交金额':
                        cell_value = round(float(cell_value), 4)                                                               
                    cell_dict[key].append(cell_value)
                    
            row = 0
            stock_done_amount = 0
            
            future_count = 0
            future_done_amount = 0
            
            
            future_list = []

            future_dict = {
                '国债期货': FutureStaticStruct(),
               '黄金期货': FutureStaticStruct(),
               '铜期货': FutureStaticStruct(),
               '其他品种': FutureStaticStruct(),                                                
            }
                                    
            future_info = ''                        
            for value in cell_dict['证券类别']:
                stock_name = cell_dict['证券代码'][row]
                if '期货' in value:
                    future_count +=1
                    if stock_name not in future_list:
                        future_list.append(stock_name)

                    future_type = get_future_type_name(stock_name)

                    if future_type not in future_dict:
                        future_type = '其他品种'
                                                                                                                                    
                    if cell_dict['成交数量'][row] > 0:       
                        future_done_amount += cell_dict['成交金额'][row]              
                        if '卖出开仓' in cell_dict['委托方向'][row]:
                            if stock_name not in future_dict[future_type].mckc_:
                                future_dict[future_type].mckc_[stock_name] = cell_dict['成交数量'][row]
                            else:
                                future_dict[future_type].mckc_[stock_name] += cell_dict['成交数量'][row]
                        elif '买入开仓' in cell_dict['委托方向'][row]:  
                            if stock_name not in future_dict[future_type].mrkc_:
                                future_dict[future_type].mrkc_[stock_name] = cell_dict['成交数量'][row]
                            else:
                                future_dict[future_type].mrkc_[stock_name] += cell_dict['成交数量'][row]
                        elif '卖出平仓' in cell_dict['委托方向'][row]:
                            if stock_name not in future_dict[future_type].mcpc_:
                                future_dict[future_type].mcpc_[stock_name] = cell_dict['成交数量'][row]
                            else:
                                future_dict[future_type].mcpc_[stock_name] += cell_dict['成交数量'][row]
                        elif '买入平仓' in cell_dict['委托方向'][row]:  
                            if stock_name not in future_dict[future_type].mrpc_:
                                future_dict[future_type].mrpc_[stock_name] = cell_dict['成交数量'][row]
                            else:
                                future_dict[future_type].mrpc_[stock_name] += cell_dict['成交数量'][row]
                                        
                row += 1
                
            future_done_amount /= 10000
            
            stock_done_amount = round(stock_done_amount, 2)
            future_done_amount = round(future_done_amount, 2)
        
            
            future_info = '今日交易'
            
            if future_count > 0:
                future_info += f" {len(future_list)} 只期货,"
            future_info += f" 成交合约价值 {round(future_done_amount,2)} 万元,其中\n"
            
            
            index = 1
            for future_type, future_struct in future_dict.items():
                future_info += future_struct.get_trade_info(future_type, index)
                index += 1
                
            
            result_dict['future_info'] = future_info
                   
            return result_dict

        except Exception as e:
            logging.error(f"读取文件 量化三 成交回报 时发生错误: {e}")  
            
        return None    
    
    def read_cjhb(self, xlrd_sheet, sheet_type="量化一"):
        try:

            if sheet_type == "量化三":
                return self.read_cjhb_lhs(self, xlrd_sheet)

            cell_dict = {}            
            header_col_dict = {}
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                valid_item = ['成交数量', '成交金额', '证券代码', '委托方向', '证券类别']                
                if cell_value in valid_item:
                    header_col_dict[cell_value] = col
                    cell_dict[cell_value] = []
                           
            for key, col in header_col_dict.items():
                for nrow in range(xlrd_sheet.nrows):
                    if nrow == 0:
                        continue
                    cell_value = str(xlrd_sheet.cell_value(nrow, col))                    
                    if key == '成交数量' or key == '成交金额':
                        cell_value = round(float(cell_value), 4)                                                               
                    cell_dict[key].append(cell_value)
                    
            row = 0
            stock_buy_count = 0
            stock_sell_count = 0
            stock_done_amount = 0
            
            future_count = 0
            option_count = 0
            future_done_amount = 0
            
            mckc = {}
            mrpc = {}
            mrkc = {}
            mcpc = {}
            
            future_list = []
            option_list = []
                                    
            future_info = ''                        
            for value in cell_dict['证券类别']:
                stock_name = cell_dict['证券代码'][row]
                
                if '股票' in value:
                    if cell_dict['委托方向'][row] == '买入':
                        stock_buy_count += 1
                    elif cell_dict['委托方向'][row] == '卖出':
                        stock_sell_count += 1
                        
                    stock_done_amount += cell_dict['成交金额'][row]
                elif '期货' in value or '期权' in value:
                    if '期货' in value:
                        future_count +=1
                        if stock_name not in future_list:
                            future_list.append(stock_name)
                            
                    elif '期权' in value:
                        option_count +=1
                        if stock_name not in option_list:
                            option_list.append(stock_name)
                            
                                                
                    future_done_amount += cell_dict['成交金额'][row]
                    
                    if cell_dict['成交数量'][row] > 0:                                        
                        if '卖出开仓' in cell_dict['委托方向'][row]:
                            if stock_name not in mckc:
                                mckc[stock_name] = cell_dict['成交数量'][row]
                            else:
                                mckc[stock_name] += cell_dict['成交数量'][row]
                        elif '买入开仓' in cell_dict['委托方向'][row]:  
                            if stock_name not in mrkc:
                                mrkc[stock_name] = cell_dict['成交数量'][row]
                            else:
                                mrkc[stock_name] += cell_dict['成交数量'][row]
                        elif '卖出平仓' in cell_dict['委托方向'][row]:
                            if stock_name not in mcpc:
                                mcpc[stock_name] = cell_dict['成交数量'][row]
                            else:
                                mcpc[stock_name] += cell_dict['成交数量'][row]
                        elif '买入平仓' in cell_dict['委托方向'][row]:  
                            if stock_name not in mrpc:
                                mrpc[stock_name] = cell_dict['成交数量'][row]
                            else:
                                mrpc[stock_name] += cell_dict['成交数量'][row]
                                        
                row += 1
                
            stock_done_amount /= 10000
            future_done_amount /= 10000
            
            stock_done_amount = round(stock_done_amount, 2)
            future_done_amount = round(future_done_amount, 2)

            stock_info = f"买入股票: {stock_buy_count} 只, 卖出股票: {stock_sell_count} 只, 股票合计成交金额: {round(stock_done_amount,2)} 万元"            
            future_info = f"今日交易: {len(future_list)} 只股指期货合约, {len(option_list)} 只股指期权合约， 成交合约价值 {round(future_done_amount,2)} 万元"
            
            future_info_2 = '今日交易'
            
            if future_count > 0:
                future_info_2 += f" {len(future_list)} 只期货合约"
            if option_count > 0:
                future_info_2 += f" {len(option_list)} 只期权合约"
            future_info_2 += f" 成交合约价值 {round(future_done_amount,2)} 万元"
            
            stock_info_2 = ''
            if stock_buy_count > 0:
                stock_info_2 += f"买入股票: {math.floor(float(stock_buy_count))} 只"
            if stock_sell_count > 0:
                stock_info_2 += f"卖出股票: {math.floor(float(stock_sell_count))} 只"
            if stock_done_amount > 0:
                stock_info_2 += f"股票合计成交金额: {round(stock_done_amount,2)} 万元"
                
            
                    
            if len(mckc) > 0:
                future_info += '\n卖出开仓: '
                future_info_2 += f"\n卖出开仓: {len(mckc)} 只"
                for key, value in mckc.items():
                    future_info += f"{key}({math.floor(value)} 手),"
            if len(mrpc) > 0:
                future_info += '\n买入平仓: '
                future_info_2 += f"\n买入平仓: {len(mrpc)} 只"
                for key, value in mrpc.items():
                    future_info += f"{key}({math.floor(value)} 手),"
            if len(mrkc) > 0:
                future_info += '\n买入开仓: '
                future_info_2 += f"\n买入开仓: {len(mrkc)} 只"
                for key, value in mrkc.items():
                    future_info += f"{key}({math.floor(value)} 手),"
            if len(mcpc) > 0:
                future_info += '\n卖出平仓: '
                future_info_2 += f"\n卖出平仓: {len(mcpc)} 只"
                for key, value in mcpc.items():
                    future_info += f"{key}({math.floor(value)} 手),"                                
                        
            result_dict = {}
            result_dict['stock_info'] = stock_info
            result_dict['future_info'] = future_info[0:len(future_info)-1]
            result_dict['stock_info_2'] = stock_info_2
            result_dict['future_info_2'] = future_info_2
            
            # print(result_dict)        
            # print(cell_dict)        
            return result_dict

        except Exception as e:
            logging.error(f"读取文件 期货保证金 时发生错误: {e}")  
            
        return None     

    def read_hzzq_drcc_lhs(self, xlrd_sheet):
        try:
            cell_dict = {}            
            header_col_dict = {}
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                valid_item = ['持仓数量',  '证券代码', '持仓多空标志', '证券类别','本币市值']          
                if cell_value in valid_item:
                    header_col_dict[cell_value] = col
                    cell_dict[cell_value] = []
                           
            for key, col in header_col_dict.items():
                for nrow in range(xlrd_sheet.nrows):
                    if nrow == 0:
                        continue
                    cell_value = str(xlrd_sheet.cell_value(nrow, col))                    
                    if key == '持仓数量'or key == '本币市值':
                        cell_value = round(float(cell_value), 4)                                                               
                    cell_dict[key].append(cell_value)
                    
            future_dict = {
                '国债期货': FutureStaticStruct(),
               '黄金期货': FutureStaticStruct(),
               '铜期货': FutureStaticStruct(),
               '其他品种': FutureStaticStruct(),                                                
            }
                                
            row = 0                       
            future_count = 0   

            done_amount = 0 # 本币市值;
                                                       
            for value in cell_dict['证券类别']:
                
                if '期货' in value and cell_dict['持仓数量'][row] > 0:
                    future_count += 1                      
                    
                    stock_name = cell_dict['证券代码'][row]                    
                    trade_type = cell_dict['持仓多空标志'][row]

                    done_amount += cell_dict['本币市值'][row]
                    
                    future_type = get_future_type_name(stock_name)

                    if future_type not in future_dict:
                        future_type = '其他品种'      
                    
                    # logging.info(f'{stock_name}, {future_type},{trade_type}, {cell_dict["本币市值"][row]}')              
                            
                    if '权利仓' in cell_dict['持仓多空标志'][row]:
                        if stock_name not in future_dict[future_type].qlc_:
                            future_dict[future_type].qlc_[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            future_dict[future_type].qlc_[stock_name] += cell_dict['持仓数量'][row]
                    elif '义务仓' in cell_dict['持仓多空标志'][row]:  
                        if stock_name not in future_dict[future_type].ywc_:
                            future_dict[future_type].ywc_[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            future_dict[future_type].ywc_[stock_name] += cell_dict['持仓数量'][row]
                    elif '多仓' in cell_dict['持仓多空标志'][row]:
                        if stock_name not in future_dict[future_type].dc_:
                            future_dict[future_type].dc_[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            future_dict[future_type].dc_[stock_name] += cell_dict['持仓数量'][row]
                    elif '空仓' in cell_dict['持仓多空标志'][row]:  
                        if stock_name not in future_dict[future_type].kc_:
                            future_dict[future_type].kc_[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            future_dict[future_type].kc_[stock_name] += cell_dict['持仓数量'][row]
                            
                row += 1

            done_amount /= 10000    
            #                                                                 
            future_info = f"共持仓: {future_count} 只期货, 持仓合约价值 {round(done_amount,2)} 万元, 其中: \n"
            
            for future_type, future_struct in future_dict.items():
                future_info += future_struct.get_hold_info(future_type)          
                       
            result_dict = {}
            result_dict['future_info'] = future_info
            
            # print(result_dict)       
            return result_dict

        except Exception as e:
            logging.error(f"读取文件 量化三 汇总证券-当日持仓 时发生错误: {e}")  
            
        return None             

    def read_hzzq_drcc(self, xlrd_sheet, sheet_type="量化一"):
        try:
            if sheet_type == "量化三":
                return self.read_hzzq_drcc_lhs(self, xlrd_sheet)
            cell_dict = {}            
            header_col_dict = {}
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                valid_item = ['持仓数量',  '证券代码', '持仓多空标志', '证券类别','本币市值']              
                if cell_value in valid_item:
                    header_col_dict[cell_value] = col
                    cell_dict[cell_value] = []
                           
            for key, col in header_col_dict.items():
                for nrow in range(xlrd_sheet.nrows):
                    if nrow == 0:
                        continue
                    cell_value = str(xlrd_sheet.cell_value(nrow, col))                    
                    if key == '持仓数量' or key == '本币市值':
                        cell_value = round(float(cell_value), 4)                                                               
                    cell_dict[key].append(cell_value)
                    
            row = 0            
            stock_count = 0
            
            future_count = 0
            option_count = 0
                                    
            future_info = ''     
            done_detail_dict = {}
            
            mckc = {} #权利仓
            mckc_count = 0
            mrpc = {} #义务仓
            mrpc_count = 0
            mrkc = {} #多仓
            mrkc_count = 0
            mcpc = {} #空仓
            mcpc_count = 0      

            done_amount = 0 # 本币市值;      
                               
            for value in cell_dict['证券类别']:
                if '股票' in value:                    
                    if cell_dict['持仓数量'][row] > 0:
                        stock_count += 1
                elif '期货' in value or '期权' in value:
                    if '期货' in value and cell_dict['持仓数量'][row] > 0:
                        future_count += 1
                    elif '期权' in value and cell_dict['持仓数量'][row] > 0:
                        option_count += 1                        

                    done_amount += cell_dict['本币市值'][row]
                    
                    stock_name = cell_dict['证券代码'][row]                    
                    trade_type = cell_dict['持仓多空标志'][row]

                    # print(f'{sheet_type}, {stock_name}, {trade_type}, {cell_dict["本币市值"][row]}')
                    
                    if stock_name not in done_detail_dict:
                        done_detail_dict[stock_name] = {}
                        done_detail_dict[stock_name][trade_type] = float(cell_dict['持仓数量'][row])
                    else:
                        if trade_type not in done_detail_dict[stock_name]:
                            done_detail_dict[stock_name][trade_type] = float(cell_dict['持仓数量'][row])
                        else:
                            done_detail_dict[stock_name][trade_type] += float(cell_dict['持仓数量'][row])
                            
                    if '权利仓' in cell_dict['持仓多空标志'][row]:
                        if stock_name not in mckc:
                            mckc[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            mckc[stock_name] += cell_dict['持仓数量'][row]
                        mckc_count += cell_dict['持仓数量'][row]
                    elif '义务仓' in cell_dict['持仓多空标志'][row]:  
                        if stock_name not in mrkc:
                            mrkc[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            mrkc[stock_name] += cell_dict['持仓数量'][row]
                        # print('持仓数量', cell_dict['持仓数量'][row], '股票名称', stock_name)
                        mrkc_count += cell_dict['持仓数量'][row]
                    elif '多仓' in cell_dict['持仓多空标志'][row]:
                        if stock_name not in mcpc:
                            mcpc[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            mcpc[stock_name] += cell_dict['持仓数量'][row]
                        mcpc_count += cell_dict['持仓数量'][row]
                    elif '空仓' in cell_dict['持仓多空标志'][row]:  
                        if stock_name not in mrpc:
                            mrpc[stock_name] = cell_dict['持仓数量'][row]
                        else:
                            mrpc[stock_name] += cell_dict['持仓数量'][row]
                        mrpc_count += cell_dict['持仓数量'][row]
                                                                    
                    
                    
                row += 1

            done_amount /= 10000
            # print(done_detail_dict)
                
            stock_info = f"股票: {stock_count} 只"            
            future_info = f"当前持有: {future_count} 只股指期货合约, {option_count} 只股指期权合约, 持仓合约价值 { round(done_amount,2) } 万元, 其中: \n"
            # print(future_info)
            if len(mckc) > 0 and mckc_count > 0:
                future_info += '\n权利仓: '
                for key, value in mckc.items():
                    if value > 0:
                        future_info += f"{key}({math.floor(float(value))} 手),"
                                                
            if len(mrkc) > 0 and mrkc_count > 0:
                future_info += '\n义务仓: '
                for key, value in mrkc.items():
                    if value > 0:
                        future_info += f"{key}({math.floor(float(value))} 手),"
                        
            if len(mcpc) > 0 and mcpc_count > 0:
                future_info += '\n多仓: '
                for key, value in mcpc.items():
                    if value > 0:
                        future_info += f"{key}({math.floor(float(value))} 手),"       
                        
            if len(mrpc) > 0 and mrpc_count > 0:
                future_info += '\n空仓: '
                for key, value in mrpc.items():
                    if value > 0:
                        future_info += f"{key}({math.floor(float(value))} 手),"             
            
            trade_detail_dict = {}
            trade_sum_dict = {}
            future_count = 0
            
            for stock_name, trade_dict in done_detail_dict.items():
                for trade_type, trade_count in trade_dict.items():
                    if trade_count > 0:                        
                        if trade_type not in trade_detail_dict:
                            trade_detail_dict[trade_type] = 1
                            future_count += 1
                        else:
                            trade_detail_dict[trade_type] += 1
                            future_count += 1
                            
                        if stock_name not in trade_sum_dict:
                            trade_sum_dict[stock_name] = trade_count
                                                                  
            result_dict = {}

            
            future_info_2 = f"共持仓 {math.floor(float(future_count))}只期货， 持仓合约价值 { round(done_amount,2) } 万元, 其中"

            # print(future_info_2)
            
            for key, value in trade_detail_dict.items():
                future_info_2 += f"{key}: {math.floor(float(value))} 只,"

            result_dict['stock_info'] = stock_info
            result_dict['future_info'] = future_info[0:len(future_info)-1]
            result_dict['future_info_2'] = future_info_2[0:len(future_info_2)-1]
            
            # print(result_dict)       
            return result_dict

        except Exception as e:
            logging.error(f"读取文件 汇总证券-当日持仓 时发生错误: {e}")  
            
        return None             

    def read_hzzz_hj_gp(self, xlrd_sheet, sheet_type="量化一"):
        try:
            profit_col = -1
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                if '总体盈亏' in cell_value:
                    profit_col = col
                    
            if profit_col == -1:
                logging.critical("文件中未找到总体盈亏，请检查。")
                
                            
            cell_dict = {}
            logging.info(f"读取文件 汇总证券-合计-股票 开始 {xlrd_sheet.nrows} {xlrd_sheet.ncols} ")
            for row in range(xlrd_sheet.nrows):
                for col in range(xlrd_sheet.ncols):
                    cell_value = str(xlrd_sheet.cell_value(row, col))
                    if row == xlrd_sheet.nrows - 1 and col == profit_col:
                        profit = float(cell_value)
                        profit = round(profit, 4)
            cell_dict['ztyk'] = profit
            return cell_dict
        except Exception as e:
            logging.error(f"读取文件 汇总证券-合计-股票 时发生错误: {e}")  
            
        return None 
    
     
class ExcelBase:
    def __init__(self):
        try:
            
            self.date = ''
            self.config_ = get_config()
            self.data_read_obj_ = ExcelDataRead
            if self.config_ is None:
                logging.critical("配置文件为空，请检查。")
                return None
                            
            if '量化一二所在目录' not in self.config_:
                logging.critical("配置文件中未找到 '量化一二所在目录' 字段，请检查。")
                return None
                
                
            tmp_dir = self.config_['量化一二所在目录']         
            self.file_path_ = tmp_dir.replace('\\', '/')
            
            if os.path.exists(self.file_path_) == False:
                logging.critical(f"目录不存在，请检查。{self.file_path_}")
                return None
                
                        
            if '量化一-投机单元-单元资产净值' in self.config_:                                
                self.dyzcjz_lh1_ = float(str(self.config_['量化一-投机单元-单元资产净值'])) #手动输入的单元资产净值;
                if self.dyzcjz_lh1_ is None:
                    logging.critical("配置文件中 '量化一-投机单元-单元资产净值' 字段值为空，请检查。")
            else:
                logging.critical("配置文件中未找到 '量化一-投机单元-单元资产净值' 字段，请检查。")
                
                
            if '量化二-账户资产净值'  in self.config_:                              
                self.zhzcjz_lh2_ = float(str(self.config_['量化二-账户资产净值'])) #手动输入的单元资产净值;
                if self.zhzcjz_lh2_ is None:
                    logging.critical("配置文件中 '量化二-账户资产净值' 字段值为空，请检查。")
            else:
                logging.critical("配置文件中未找到 '量化二-账户资产净值' 字段，请检查。")  
                     
                
            if '量化二-占用' in self.config_:                                            
                self.lh2_zy_ = float(str(self.config_['量化二-占用'])) #手动输入的单元资产净值;
                if self.lh2_zy_ is None:
                    logging.critical("配置文件中 '量化二-占用' 字段值为空，请检查。")
            else:
                logging.critical("配置文件中未找到 '量化二-占用' 字段，请检查。")


            if '量化三-账户资产净值'  in self.config_:                              
                self.zhzcjz_lh3_ = float(str(self.config_['量化三-账户资产净值'])) #手动输入的单元资产净值;
                if self.zhzcjz_lh3_ is None:
                    logging.critical("配置文件中 '量化三-账户资产净值' 字段值为空，请检查。")
            else:
                logging.critical("配置文件中未找到 '量化三-账户资产净值' 字段，请检查。")  

            if '量化一-总份额'  in self.config_:                                        
                self.total_amount1_ = float(str(self.config_['量化一-总份额'])) #手动输入的单元资产净值;
                if self.total_amount1_ is None:
                    logging.critical("配置文件中 '量化一-总份额' 字段值为空，请检查。")
            else:
                logging.critical("配置文件中未找到 '量化一-总份额' 字段，请检查。")    
                          
                
            if '量化二-总份额' in self.config_:                                                
                self.total_amount2_ = float(str(self.config_['量化二-总份额'])) #手动输入的单元资产净值;
                if self.total_amount2_ is None:
                    logging.critical("配置文件中 '量化二-总份额' 字段值为空，请检查。")
            else:
                logging.critical("配置文件中未找到 '量化二-总份额' 字段，请检查。")


            if '量化三-总份额' in self.config_:                                                
                self.total_amount3_ = float(str(self.config_['量化三-总份额'])) #手动输入的单元资产净值;
                if self.total_amount3_ is None:
                    logging.critical("配置文件中 '量化三-总份额' 字段值为空，请检查。")
            else:
                logging.critical("配置文件中未找到 '量化三-总份额' 字段，请检查。")                
                  
                
            if '是否绘制净值曲线' in self.config_:
                self.draw_net_value_curve_ = self.config_['是否绘制净值曲线']
            else:
                self.draw_net_value_curve_ = 0
                
            if '绘制折线图天数' in self.config_:
                self.draw_line_days_ = int(self.config_['绘制折线图天数'])
            else:
                self.draw_line_days_ = 15
                                                    
            self.target_workbook_ = Workbook()        
            
            self.jz_workbook_ = load_workbook(filename=self.file_path_ + '/净值.xlsx')
            # FCE4D3
            self.fill_ = PatternFill(start_color='FCE4D3', end_color='FCE4D3', fill_type='solid')
            self.font_ = Font(bold = True)        
            self.thin_border_ = Side(border_style='thin', color='000000')
            self.border_ = Border(left=self.thin_border_, right=self.thin_border_, top=self.thin_border_, bottom=self.thin_border_)
            
            self.src_excel_file_dict_ = {
                '量化一':{
                    '成交回报':None,
                    '单元资产':None,
                    '汇总证券-当日持仓':None,
                    '汇总证券-合计':None,
                    '汇总证券-合计-股票':None,
                    '交易所回购':None,
                    '期货保证金分析':None,
                    '其余信息': {
                        '收盘数据': {
                            
                        },
                        "结算数据": {
                            
                        },
                        'isOpen':True                        
                    }

                },
                '量化二':{
                    '成交回报':None,
                    '单元资产':None,
                    '汇总证券-当日持仓':None,
                    '汇总证券-合计':None,
                    '期货保证金分析':None,
                    '其余信息': {
                        '收盘数据': {
                            
                        },
                        "结算数据": {
                            
                        },
                        'isOpen':True                        
                    }
                },
                '量化三':{
                    '成交回报':None,
                    '单元资产':None,
                    '汇总证券-当日持仓':None,
                    '汇总证券-合计':None,
                    '期货保证金分析':None,
                    '其余信息': {
                        '收盘数据': {
                            
                        },
                        "结算数据": {
                            
                        },
                        'isOpen':True                        
                    }
                }                
            }
            
            self.src_excel_file_dict_ = self.init_excel_file(self.file_path_, self.src_excel_file_dict_)
            if self.src_excel_file_dict_ is None:
                logging.critical("初始化 Excel 文件失败。")
                          
                
            self.read_jz_info()
        except Exception as e:
            logging.error(f"读取基本信息出错: {e}")  
                     
    def init_excel_file(self, execl_file_path, file_dict):
        try:
            for key, value in file_dict.items():
                tmp_dir = execl_file_path + '/' + key
                if os.path.exists(tmp_dir) == True:                                 
                    for file_name, value1 in value.items():                    
                            if file_name != '其余信息':
                                complete_file_path = execl_file_path + '/' + key + '/' + file_name + '.xls'  
                                if os.path.exists(complete_file_path) == True:
                                    try:    
                                        tmp_workbook = xlrd.open_workbook(complete_file_path)
                                        tmp_sheet = tmp_workbook.sheet_by_index(0)
                                        logging.info(f"成功读取文件 {complete_file_path}")
                                        file_dict[key][file_name] = self.data_read_obj_.read_excel_sheet(self=self.data_read_obj_, xlrd_sheet=tmp_sheet, data_type=file_name, sheet_type=key)

                                    except FileNotFoundError:   
                                        logging.warning(f"文件 {complete_file_path} 未找到。")
                                    except Exception as e:
                                        logging.warning(f"读取文件 {complete_file_path} 时发生错误: {e}")       
                                else:
                                    logging.warning(f"文件 {complete_file_path} 未找到。")
                else:
                    file_dict[key]['其余信息']['isOpen'] = False
                    logging.warning(f"目录 {tmp_dir} 未找到。")
                    
            return file_dict                   
        except Exception as e:
            logging.error(f"初始化 Excel 文件出错: {e}")  
            return None
             
    def read_jz_info(self):
        try:
            if '量化一-结算数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化一-结算数据']
                self.last_jz1_1_ = get_last_jz(sheet, '量化一-结算数据')
                self.all_jz_1_1_ = get_all_jz_info(sheet, '量化一-结算数据')
                self.all_jz_1_1_['hc_list'] = get_row(sheet, '量化一-结算数据', 3)
                if g_test_pic:
                    self.all_jz_1_1_, self.last_jz1_1_ = get_test_data()
                
            else:   
                logging.critical("文件中未找到 量化一-结算数据 表格，请检查。")
                
            
            
            if '量化一-收盘数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化一-收盘数据']
                row_dict = {}
                self.last_jz1_2_ = get_last_jz(sheet, '量化一-收盘数据')
                self.all_jz_1_2_ = get_all_jz_info(sheet, '量化一-收盘数据')
                self.all_jz_1_2_['hc_list'] = get_row(sheet, '量化一-收盘数据', 3)
                if g_test_pic:
                    self.all_jz_1_2_, self.last_jz1_2_ = get_test_data()
                                
                # print('self.all_jz_1_2_:', self.all_jz_1_2_)
            else:
                logging.critical("文件中未找到 量化一-收盘数据 表格，请检查。")
                
                
                            
            if '量化二-结算数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化二-结算数据']
                row_dict = {}
                self.jz2_1_ = get_last_jz(sheet, '量化二-结算数据')
                self.all_jz_2_1_ = get_all_jz_info(sheet, '量化二-结算数据')
                self.all_jz_2_1_['hc_list'] = get_row(sheet, '量化二-结算数据', 3)
                if g_test_pic:
                    self.all_jz_2_1_, self.jz2_1_ = get_test_data()            
                # print('self.all_jz_1_2_:', self.all_jz_2_1_)
            else:
                logging.critical("文件中未找到 量化二-结算数据 表格，请检查。")
                
                
            if '量化二-收盘数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化二-收盘数据']
                row_dict = {}
                self.jz2_2_ = get_last_jz(sheet, '量化二-收盘数据')
                self.all_jz_2_2_ = get_all_jz_info(sheet, '量化二-收盘数据')
                self.all_jz_2_2_['hc_list'] = get_row(sheet, '量化二-收盘数据', 3)
                if g_test_pic:
                    self.all_jz_2_2_, self.jz2_2_ = get_test_data()  
                                
            else:
                logging.critical("文件中未找到 量化二-收盘数据 表格，请检查。")

            if '量化三-结算数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化三-结算数据']
                row_dict = {}
                self.jz3_1_ = get_last_jz(sheet, '量化三-结算数据')
                self.all_jz_3_1_ = get_all_jz_info(sheet, '量化三-结算数据')
                self.all_jz_3_1_['hc_list'] = get_row(sheet, '量化三-结算数据', 3)
                # logging.info(f"self.all_jz_3_1_:{self.all_jz_3_1_}")
                if g_test_pic:
                    self.all_jz_3_1_, self.jz3_1_ = get_test_data()            
                # print('self.all_jz_1_2_:', self.all_jz_2_1_)
            else:
                logging.critical("文件中未找到 量化三-结算数据 表格，请检查。")
                
                
            if '量化三-收盘数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化三-收盘数据']
                row_dict = {}
                self.jz3_2_ = get_last_jz(sheet, '量化三-收盘数据')
                self.all_jz_3_2_ = get_all_jz_info(sheet, '量化三-收盘数据')
                self.all_jz_3_2_['hc_list'] = get_row(sheet, '量化三-收盘数据', 3)
                if g_test_pic:
                    self.all_jz_3_2_, self.jz3_2_ = get_test_data()                              
            else:
                logging.critical("文件中未找到 量化三-收盘数据 表格，请检查。")                
                        
        except Exception as e:
            logging.error(f"读取净值信息出错: {e}")  
                                    
    def reset_date(self, date_list):
        new_date = []
        try:            
            time_format = '%Y-%m-%d'
            if len(date_list) > x_label_count and len(date_list) <= 2*x_label_count:
                time_format = '%m-%d'
            for tmp_date in date_list:
                if ':' in tmp_date:
                    dt = datetime.strptime(tmp_date, '%Y-%m-%d %H:%M:%S')
                    # 格式化为 '04-03' 的形式
                    result = dt.strftime(time_format) 
                    new_date.append(result)        
                elif '-' in tmp_date:
                    dt = datetime.strptime(tmp_date, '%Y-%m-%d')
                    # 格式化为 '04-03' 的形式
                    result = dt.strftime(time_format) 
                    new_date.append(result)                 
                elif '/' in tmp_date:
                    dt = datetime.strptime(tmp_date, '%Y/%m/%d')
                    # 格式化为 '04-03' 的形式
                    result = dt.strftime(time_format) 
                    new_date.append(result)                 
                else:
                    new_date.append(tmp_date)
        except Exception as e:
            logging.error(f"重置日期格式出错: {e}")  
                
        return new_date
       
    def draw_save_pic(self, data, sheet, pic_name):
        try:
            
            if self.draw_net_value_curve_ == 0:
                return
            # 绘制折线图
            new_date = self.reset_date(data['date'])
            net_value_list = data['unit_net_value']
            hc_list = data['hc_list'] # 计算最大回撤
            
            if g_test_pic:
                test_len = len(new_date) - 1
                new_date = new_date[0:test_len]
                net_value_list = net_value_list[0:test_len]
                hc_list = hc_list[0:test_len]
                
            max_hc = 0
            min_hc = min(hc_list)
            
            if min_hc == 0:
                min_hc = -0.05
                max_hc = 0
            
            max_net_value = max(net_value_list)
            min_net_value = min(net_value_list)
            
            delta = max_net_value - min_net_value
                        
            # print(new_date)
            plt.figure(figsize=(10, 6)) 
            
                    
            df = pd.DataFrame({
                'date': new_date,
                'net_value': net_value_list,
                'drawdown': hc_list
            })
            
            index_list, date_list = get_resize_index(new_date, 6)

            # 绘图设置
            fig, ax1 = plt.subplots(figsize=(10, 6))

            # 绘制策略净值曲线
            color = 'tab:blue'
            ax1.set_xlabel('日期')
            ax1.set_ylabel('净值', color=color)
            ax1.plot(df['date'], df['net_value'], label='策略净值', color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_ylim(ymin=min_net_value-delta*0.1, ymax=max_net_value+delta*0.1)
            ax1.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
            
            # if pic_name == '量化三-收盘数据':
            #     logging.info(f"净值数据为: {df['net_value']}, min_net_value: {min_net_value}, max_net_value: {max_net_value}, delta: {delta}")            
            
                        
            # 创建第二个y轴用于绘制回撤
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('回撤', color=color)
            
            # alpha = 0.1, 

            logging.info(f"回撤数据为: {df['drawdown']}, min_hc: {min_hc}, max_hc: {max_hc}")
            
            if len(hc_list) < self.draw_line_days_:
                ax2.bar(df['date'], df['drawdown'], width=0.01, color='red', alpha = 0.5, edgecolor='red', label='回撤')
                ax2.set_ylim(ymin=min_hc*2, ymax=max_hc)
                ax2.tick_params(axis='y', labelcolor=color)
            else:
                ax2.fill_between(df['date'], 0.2, df['drawdown'], label='回撤', alpha = 0.5, edgecolor='red', color=color)
                ax2.tick_params(axis='y', labelcolor=color)
                ax2.set_ylim(ymin=min_hc*2, ymax=max_hc)
                
            # 设置刻度位置
            ax1.xaxis.set_major_locator(FixedLocator(index_list))
            # 设置刻度标签
            ax1.xaxis.set_major_formatter(FixedFormatter(date_list))     
            
            # ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)      
            
            ax2.xaxis.set_major_locator(FixedLocator(index_list))
            # 设置刻度标签
            ax2.xaxis.set_major_formatter(FixedFormatter(date_list))      
            
            ax2.yaxis.set_major_formatter(PercentFormatter(1))

            
            # ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)               

            # 设置x轴日期格式
            # if len(hc_list) < 20:
            #     ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

            # 添加标题和图例
            plt.title('策略净值与回撤')
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper left', bbox_to_anchor=(0, 0.93))

            # 调整布局
            plt.tight_layout()
            # plt.show()
            file_name = self.file_path_ + '/' + pic_name + '.png'
            
            # plt.xticks(rotation = 90)
            # plt.xticks(index_list, date_list)
            # 保存图片
            plt.savefig(file_name)  
            
            plt.close() 
            

            
            if self.draw_net_value_curve_ > 0:            
                img = Image(file_name)
                img.anchor = 'E2'
                sheet.add_image(img)
                
        except Exception as e:
            logging.error(f"绘制 {pic_name} 图时发生错误: {e}")  
                                                                                                    
    def set_new_jz_info(self):
        try:
            dt = datetime.strptime(self.date, '%Y-%m-%d')
            tmp_date = dt.strftime('%Y/%m/%d')
                                
            if self.src_excel_file_dict_['量化一']['其余信息']['isOpen'] is True:
                if '量化一-结算数据' in self.jz_workbook_.sheetnames:
                    sheet = self.jz_workbook_['量化一-结算数据']
                    last_row = get_last_row(sheet, '量化一-结算数据')
                    sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                    sheet.cell(row = last_row+1, column = 2, value = round(self.new_jz_1_1_, 5))
                    
                    for i in range(0, last_row):
                        sheet.cell(row = i+2, column = 3, value = str(round(self.all_jz_1_1_['hc_list'][i]*100, 4)) + '%')
                else:
                    logging.critical("文件中未找到 量化一-结算数据 表格，请检查。")
                    
                if '量化一-收盘数据' in self.jz_workbook_.sheetnames:
                    sheet = self.jz_workbook_['量化一-收盘数据']
                    last_row = get_last_row(sheet, '量化一-收盘数据')
                    sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                    sheet.cell(row = last_row+1, column = 2, value = round(self.new_jz_1_2_, 5))
                    
                    for i in range(0, last_row):       
                        sheet.cell(row = i+2, column = 3, value = str(round(self.all_jz_1_2_['hc_list'][i]*100, 4)) + '%')
                else:
                    logging.critical("文件中未找到 量化一-收盘数据 表格，请检查。")
            
            if self.src_excel_file_dict_['量化二']['其余信息']['isOpen'] is True:
                if '量化二-结算数据' in self.jz_workbook_.sheetnames:
                    sheet = self.jz_workbook_['量化二-结算数据']
                    last_row = get_last_row(sheet, '量化二-结算数据')
                    sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                    sheet.cell(row = last_row+1, column = 2, value = round(self.new_jz_2_1_, 5))
                    
                    for i in range(0, last_row):    
                        sheet.cell(row = i+2, column = 3, value = str(round(self.all_jz_2_1_['hc_list'][i]*100, 4)) + '%')
                else:
                    logging.critical("文件中未找到 量化二-结算数据 表格，请检查。")
                    
                if '量化二-收盘数据' in self.jz_workbook_.sheetnames:
                    sheet = self.jz_workbook_['量化二-收盘数据']
                    last_row = get_last_row(sheet, '量化二-收盘数据')
                    sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                    sheet.cell(row = last_row+1, column = 2, value = round(self.new_jz_2_2_,5))
                    
                    for i in range(0, last_row):    
                        sheet.cell(row = i+2, column = 3, value = str(round(self.all_jz_2_2_['hc_list'][i]*100, 4)) + '%')   
                else:
                    logging.critical("文件中未找到 量化二-收盘数据 表格，请检查。")        

            if self.src_excel_file_dict_['量化三']['其余信息']['isOpen'] is True:
                if '量化三-结算数据' in self.jz_workbook_.sheetnames:
                    sheet = self.jz_workbook_['量化三-结算数据']
                    last_row = get_last_row(sheet, '量化三-结算数据')
                    sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                    sheet.cell(row = last_row+1, column = 2, value = round(self.new_jz_3_1_, 5))
                    
                    for i in range(0, last_row):  
                        sheet.cell(row = i+2, column = 3, value = str(round(self.all_jz_3_1_['hc_list'][i]*100, 4)) + '%')
                else:
                    logging.critical("文件中未找到 量化三-结算数据 表格，请检查。")
                    
                if '量化三-收盘数据' in self.jz_workbook_.sheetnames:
                    sheet = self.jz_workbook_['量化三-收盘数据']
                    last_row = get_last_row(sheet, '量化三-收盘数据')
                    sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                    sheet.cell(row = last_row+1, column = 2, value = round(self.new_jz_3_2_,5))
                    
                    for i in range(0, last_row):    
                        sheet.cell(row = i+2, column = 3, value = str(round(self.all_jz_3_2_['hc_list'][i]*100, 4)) + '%')   
                else:
                    logging.critical("文件中未找到 量化三-收盘数据 表格，请检查。")                                          
            
            self.jz_workbook_.save(self.file_path_ + '/净值.xlsx')
        except Exception as e:
            logging.error(f"设置新净值信息出错: {e}")  
                        
    def Work(self):
        # print(self.src_excel_file_dict_)
        if self.src_excel_file_dict_['量化一']['其余信息']['isOpen'] is True:
            self.gene_first_sheet()
            self.gene_second_sheet()
           
        if self.src_excel_file_dict_['量化二']['其余信息']['isOpen'] is True:
            self.gene_third_sheet()
            self.gene_fourth_sheet()     

        if self.src_excel_file_dict_['量化三']['其余信息']['isOpen'] is True:
            self.gene_fivth_sheet()
            self.gene_sixth_sheet()    
            # pass         
                    
        sheet_name_to_delete = 'Sheet'
        if sheet_name_to_delete in self.target_workbook_.sheetnames:
            sheet = self.target_workbook_[sheet_name_to_delete]
            self.target_workbook_.remove(sheet)
            logging.info(f"{sheet_name_to_delete} 已成功删除。")
        else:
            logging.warning(f"{sheet_name_to_delete} 不存在。")
            
        file_name = self.file_path_ + '/量化业务日报-' + self.date + '.xlsx'    
        logging.info(f"目标文件名: {file_name}")   
                 
        self.target_workbook_.save(file_name)
        
        self.set_new_jz_info()
            
    def gene_first_sheet(self):
        try:
            sheet = self.target_workbook_.create_sheet(title='量化一-结算数据')
            self.sheet_1_row_dict_ = {
                '统计日期':1,
                '一、账户资产及收益情况':2,
                '账户名称':3,
                '账户编号':4,
                '资产单元名称':5,
                '单元资产净值':6,
                '账户资产净值':7,
                '交易所回购':8,
                '总盈利/亏损（不含逆回购）':9,
                '收益率（不含逆回购）':10,
                '总盈利/亏损（含逆回购）':11,
                '收益率（含逆回购）':12,
                '二、净值列示':13,
                '实收资本':14,
                '资产净值':15,
                '总份额':16,
                '期初单位净值':17,
                '昨日单位净值':18,
                '单位净值':19,
                '日净值增长率':20,
                '三、保证金使用情况':21,
                '占用':22,
                '账户权益':23,
                '风险度':24,
                '四、交易情况':25,
                '交易方向及数量':26,
                '五、持仓情况':27,
                '持仓品种及数量':28,
                '注释':29
            }
            
            merge_col_list = ['账户名称', '账户编号', '账户资产净值', '总盈利/亏损（不含逆回购）', '收益率（不含逆回购）','总盈利/亏损（含逆回购）','收益率（含逆回购）',
                                '实收资本', '资产净值', '总份额', '期初单位净值', '昨日单位净值', '单位净值', '日净值增长率']
            
            for key, value in self.sheet_1_row_dict_.items():
                if value is not None:
                    if key != '统计日期' and key != '注释':
                        sheet.cell(row = value, column = 1, value = key).font = self.font_
                        sheet.cell(row = value, column = 1, value = key).border = self.border_
                    else:
                        sheet.cell(row = value, column = 1, value = key)
            
            sheet.cell(row = self.sheet_1_row_dict_['统计日期'], column = 3, value = "（金额单位：元）")        
            sheet.cell(row = self.sheet_1_row_dict_['一、账户资产及收益情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_1_row_dict_['二、净值列示'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_1_row_dict_['三、保证金使用情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_1_row_dict_['四、交易情况'], column = 1).fill = self.fill_        
            sheet.cell(row = self.sheet_1_row_dict_['五、持仓情况'], column = 1).fill = self.fill_
                            
            cell_count = 1             
            cell_col_index = {}
            zhzcjz = 0
            if self.src_excel_file_dict_['量化一']['单元资产'] is not None:
                cell_index = 1
                for key, value in self.src_excel_file_dict_['量化一']['单元资产'].items():
                    if key != '合计':
                        
                        dt = datetime.strptime(value['统计日期'], '%Y-%m-%d')
                        self.date = dt.strftime('%Y-%m-%d')
                                        
                        set_value(sheet, 1,2,'统计日期', value, '量化一-单元资产',False)
                                                                
                        set_value(sheet, self.sheet_1_row_dict_['账户名称'], 2,'账户名称', value, '量化一-单元资产',False, self.border_)
                        tmpzhbh = value['账户编号']
                        sheet.cell(row = self.sheet_1_row_dict_['账户编号'], column = 2, value=math.floor(float(tmpzhbh))).border = self.border_
                        set_value(sheet, self.sheet_1_row_dict_['资产单元名称'],1+cell_index,'资产单元名称', value, '量化一-单元资产',False, self.border_)
                        set_value(sheet, self.sheet_1_row_dict_['单元资产净值'],1+cell_index,'单元资产净值(净价)', value, '量化一-单元资产', True,self.border_)
                        cell_index += 1
                        cell_col_index[key] = cell_index                        
                                            
                        zhzcjz += float(value['单元资产净值(净价)'])                
                    else :
                        set_value(sheet, self.sheet_1_row_dict_['账户资产净值'],2,'单元资产净值(净价)', value, '量化一-单元资产',False, self.border_)
                        zhzcjz = float(value['单元资产净值(净价)'])
                # print(cell_col_index)
                cell_count = cell_index
                
                sheet.cell(row = self.sheet_1_row_dict_['账户资产净值'], column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet_1_row_dict_['账户资产净值'], column = 2).border = self.border_

            else:
                logging.warning("量化一-单元资产文件不存在。")
                
            jyshg_profit = 0 # 交易所回购
            if self.src_excel_file_dict_['量化一']['交易所回购'] is not None:
                if 'profit' in self.src_excel_file_dict_['量化一']['交易所回购']:   
                    jyshg_profit = self.src_excel_file_dict_['量化一']['交易所回购']['profit']
                    sheet.cell(row = self.sheet_1_row_dict_['交易所回购'], column = cell_col_index['权益类一单元'], value =jyshg_profit).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_1_row_dict_['交易所回购'], column = cell_col_index['权益类一单元']).border = self.border_
                    
                    sheet.cell(row = self.sheet_1_row_dict_['交易所回购'], column = cell_col_index['量化一-投机单元'], value ='-')
                else:
                    logging.warning("量化一-交易所回购文件不存在。")
            else:
                logging.warning("量化一-交易所回购文件不存在。")
        
            profits1 = 0  #总盈利/亏损（不含逆回购）
            if self.src_excel_file_dict_['量化一']['汇总证券-合计'] is not None:
                if 'profit' in self.src_excel_file_dict_['量化一']['汇总证券-合计']:
                    profits1 = self.src_excel_file_dict_['量化一']['汇总证券-合计']['profit']
                    sheet.cell(row = self.sheet_1_row_dict_['总盈利/亏损（不含逆回购）'], column = 2, value = str(profits1)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_1_row_dict_['总盈利/亏损（不含逆回购）'], column = 2).border = self.border_
                    value2 = profits1 / 3000 / 10000 * 100
                    value2 = round(value2, 4)
                    sheet.cell(row = self.sheet_1_row_dict_['收益率（不含逆回购）'], column = 2, value = str(value2)+"%")
                    sheet.cell(row = self.sheet_1_row_dict_['收益率（不含逆回购）'], column = 2).border = self.border_
                    
                    profits2 = zhzcjz - 30000000 #总盈利/亏损（含逆回购）
                    profits2 = round(profits2, 2)
                    sheet.cell(row = self.sheet_1_row_dict_['总盈利/亏损（含逆回购）'], column = 2, value = str(profits2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_1_row_dict_['总盈利/亏损（含逆回购）'], column = 2).border = self.border_
                    value3 = profits2 / 3000 / 10000 * 100 # 收益率（含逆回购）
                    value3 = round(value3, 4)
                    sheet.cell(row = self.sheet_1_row_dict_['收益率（含逆回购）'], column = 2, value = str(value3)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_1_row_dict_['收益率（含逆回购）'], column = 2).border = self.border_
                    
                else:
                    logging.warning("量化一-汇总证券-合计文件不存在。")
            else:
                logging.warning("量化一-汇总证券-合计文件不存在。")
                
            sszb = 3000*10000
            qcdwjz = sszb/self.total_amount1_ #期初单位净值
            dwjz = zhzcjz/self.total_amount1_ #单位净值
            
            sheet.cell(row = self.sheet_1_row_dict_['实收资本'], column = 2, value = sszb).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_1_row_dict_['资产净值'], column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_1_row_dict_['总份额'], column = 2, value = self.total_amount1_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_1_row_dict_['期初单位净值'], column = 2, value = round(qcdwjz, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_1_row_dict_['昨日单位净值'], column = 2, value = round(self.last_jz1_1_, 5))
            sheet.cell(row = self.sheet_1_row_dict_['单位净值'], column = 2, value = round(dwjz, 5))
            sheet.cell(row = self.sheet_1_row_dict_['日净值增长率'], column = 2, value = str(round((dwjz - self.last_jz1_1_)/self.last_jz1_1_*100, 5)) + '%')  
            
            sheet.cell(row = self.sheet_1_row_dict_['实收资本'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_1_row_dict_['资产净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_1_row_dict_['总份额'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_1_row_dict_['期初单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_1_row_dict_['昨日单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_1_row_dict_['单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_1_row_dict_['日净值增长率'], column = 2).border = self.border_
            self.new_jz_1_1_ = round(dwjz, 5)
                
            if self.src_excel_file_dict_['量化一']['期货保证金分析'] is not None:
                for key, value in self.src_excel_file_dict_['量化一']['期货保证金分析'].items():
                    if key in cell_col_index:
                        set_value(sheet, self.sheet_1_row_dict_['占用'],cell_col_index[key],'占用保证金(静态)', value, '量化一-期货保证金分析',True, self.border_)
                        set_value(sheet, self.sheet_1_row_dict_['账户权益'],cell_col_index[key],'账户权益', value, '量化一-期货保证金分析', True, self.border_)                    
                        sheet.cell(row = self.sheet_1_row_dict_['风险度'], column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),3))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet_1_row_dict_['风险度'], column = cell_col_index[key]).border = self.border_
                    else:
                        logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                        
                sheet.cell(row = self.sheet_1_row_dict_['占用'], column = 3, value="-").border = self.border_
                sheet.cell(row = self.sheet_1_row_dict_['账户权益'], column = 3,value="-").border = self.border_
                sheet.cell(row = self.sheet_1_row_dict_['风险度'], column = 3,value="-").border = self.border_
            else:
                logging.warning("量化一-期货保证金分析文件不存在。")
                
            if self.src_excel_file_dict_['量化一']['成交回报'] is not None:
                set_value(sheet, self.sheet_1_row_dict_['交易方向及数量'],2,'future_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
                set_value(sheet, self.sheet_1_row_dict_['交易方向及数量'],3,'stock_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
            else:
                logging.warning("量化一-成交回报文件不存在。")
                
            if self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet_1_row_dict_['持仓品种及数量'],2,'future_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓',False, self.border_)
                set_value(sheet, self.sheet_1_row_dict_['持仓品种及数量'],3,'stock_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
            else:
                logging.warning("量化一-汇总证券-当日持仓文件不存在。")             
            
            extra_info = f"注:\n1、总盈利/亏损(不含逆回购): 根据032盈亏数据计算,未扣除中金所申报费。\n"
            extra_info += f"2、总盈利/亏损（含逆回购）：已扣除中金所申报费；按照O32盈亏数据计算的未扣除申报费的金额为：{round(jyshg_profit + profits1,4)} 元。\n"
            sheet.cell(row = self.sheet_1_row_dict_['注释'], column = 1, value = extra_info)

        
            set_sheet_middle(sheet)

            sheet.column_dimensions['A'].width = 26
            # 设置第二列（B列）的宽度为10个字符
            sheet.column_dimensions['B'].width = 58
            # 设置第三列（C列）的宽度为15个字符
            sheet.column_dimensions['C'].width = 58        

            for key, value in self.sheet_1_row_dict_.items():
                if key == '交易方向及数量' or key == '持仓品种及数量':
                    sheet.row_dimensions[value].height = 140 
                elif key == '注释':
                    sheet.row_dimensions[value].height = 60
                else:
                    sheet.row_dimensions[value].height = 32
            
            sheet.cell(row = self.sheet_1_row_dict_['交易方向及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
            sheet.cell(row = self.sheet_1_row_dict_['交易方向及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
            sheet.cell(row = self.sheet_1_row_dict_['持仓品种及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
            sheet.cell(row = self.sheet_1_row_dict_['持仓品种及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            sheet.cell(row = self.sheet_1_row_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            
            for key, value in self.sheet_1_row_dict_.items():
                if '注释' in key or '、' in key:
                    sheet.merge_cells(start_row=value, start_column=1, end_row=value, end_column=cell_count)
                elif key in merge_col_list:
                    sheet.merge_cells(start_row=value, start_column=2, end_row=value, end_column=cell_count)
                    
            self.all_jz_1_1_['date'].append(self.date)
            self.all_jz_1_1_['unit_net_value'].append(self.new_jz_1_1_)       
            # logging.info(f"{self.all_jz_1_1_['hc_list']}")
            self.all_jz_1_1_['hc_list'] = calc_max_drawdown(self.all_jz_1_1_['unit_net_value'], self.all_jz_1_1_['hc_list']) 
            # logging.info(f"{self.all_jz_1_1_['hc_list']}")
            self.draw_save_pic(self.all_jz_1_1_, sheet, '量化一-收盘数据')     
        except Exception as e:
            logging.error(f"生成 量化一-结算数据 表格时发生错误: {e}")             
                
    def gene_second_sheet(self):
        try:
            sheet = self.target_workbook_.create_sheet(title='量化一-收盘数据')
            self.sheet_2_row_dict_ = {
                '统计日期':1,
                '一、账户资产及收益情况':2,
                '账户名称':3,
                '账户编号':4,
                '资产单元名称':5,
                '单元资产净值':6,
                '账户资产净值':7,
                '交易所回购':8,
                '盈利/亏损（不含逆回购）':9,
                '总盈利/亏损（不含逆回购）':10,
                '收益率（不含逆回购）':11,
                '盈利/亏损（含逆回购）':12,
                '总盈利/亏损（含逆回购）':13,
                '收益率（含逆回购）':14,
                '二、净值列示':15,
                '实收资本':16,
                '资产净值':17,
                '总份额':18,
                '期初单位净值':19,
                '昨日单位净值':20,
                '单位净值':21,
                '日净值增长率':22,
                '三、保证金使用情况':23,
                '占用':24,
                '账户权益':25,
                '风险度':26,
                '四、交易情况':27,
                '交易方向及数量':28,
                '五、持仓情况':29,
                '持仓品种及数量':30,
                '注释':31
            }
        
            merge_col_list = ['账户名称', '账户编号', '账户资产净值',  '总盈利/亏损（不含逆回购）', '收益率（不含逆回购）',
                            '总盈利/亏损（含逆回购）','收益率（含逆回购）',
                                '实收资本', '资产净值', '总份额', '期初单位净值', '昨日单位净值', '单位净值', '日净值增长率']
                    
            for key, value in self.sheet_2_row_dict_.items():
                if value is not None:
                    if key != '统计日期' and key != '注释':
                        sheet.cell(row = value, column = 1, value = key).font = self.font_
                        sheet.cell(row = value, column = 1, value = key).border = self.border_
                    else:
                        sheet.cell(row = value, column = 1, value = key)

            sheet.cell(row = 1, column = 3, value = "（金额单位：元）")
            
            sheet.cell(row = self.sheet_2_row_dict_['统计日期'], column = 3, value = "（金额单位：元）")        
            sheet.cell(row = self.sheet_2_row_dict_['一、账户资产及收益情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_2_row_dict_['二、净值列示'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_2_row_dict_['三、保证金使用情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_2_row_dict_['四、交易情况'], column = 1).fill = self.fill_        
            sheet.cell(row = self.sheet_2_row_dict_['五、持仓情况'], column = 1).fill = self.fill_
                    
            
        
            cell_count = 1             
            cell_col_index = {}
            zhzcjz = 0 #账户资产净值;
            hzzq_hegp_ztyk = 0 #汇总证券-合计-股票 总体盈亏
            if self.src_excel_file_dict_['量化一']['汇总证券-合计-股票'] is not None:
                if 'ztyk' in self.src_excel_file_dict_['量化一']['汇总证券-合计-股票']:
                    hzzq_hegp_ztyk = round(float(self.src_excel_file_dict_['量化一']['汇总证券-合计-股票']['ztyk']),2)
                else:
                    logging.warning("量化一-汇总证券-合计-股票文件不存在。")
            else:
                logging.warning("量化一-汇总证券-合计-股票文件不存在。")
            
            if self.src_excel_file_dict_['量化一']['单元资产'] is not None:
                cell_index = 1
                for key, value in self.src_excel_file_dict_['量化一']['单元资产'].items():
                    if key != '合计':
                        set_value(sheet, self.sheet_2_row_dict_['统计日期'],2,'统计日期', value, '量化一-单元资产', False)
                        set_value(sheet, self.sheet_2_row_dict_['账户名称'],2,'账户名称', value, '量化一-单元资产', False,self.border_)
                        tmpzhbh =  re.sub(r'\.0$', '', value['账户编号'])
                        sheet.cell(row = self.sheet_2_row_dict_['账户编号'], column = 2, value=tmpzhbh).border = self.border_
                        if '量化一-投机单元' in key:
                            sheet.cell(row = self.sheet_2_row_dict_['单元资产净值'], column = 1+cell_index, value=self.dyzcjz_lh1_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 单元资产净值 = 手动输入
                            sheet.cell(row = self.sheet_2_row_dict_['单元资产净值'], column = 1+cell_index).border = self.border_
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（不含逆回购）'], column = 1+cell_index, value=self.dyzcjz_lh1_-6000000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（不含逆回购） = 单元资产净值-600万元
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（不含逆回购）'], column = 1+cell_index).border = self.border_
                        # set_value(sheet, self.sheet_2_row_dict_['账户编号'],2,'账户编号', value, '量化一-单元资产', False, self.border_)
                        set_value(sheet, self.sheet_2_row_dict_['资产单元名称'],1+cell_index,'资产单元名称', value, '量化一-单元资产', False, self.border_)
                        if '量化一-投机单元' in key:
                            sheet.cell(row = self.sheet_2_row_dict_['单元资产净值'], column = 1+cell_index, value=self.dyzcjz_lh1_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 单元资产净值 = 手动输入
                            sheet.cell(row = self.sheet_2_row_dict_['单元资产净值'], column = 1+cell_index).border = self.border_
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（不含逆回购）'], column = 1+cell_index, value=self.dyzcjz_lh1_-6000000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（不含逆回购） = 单元资产净值-600万元
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（不含逆回购）'], column = 1+cell_index).border = self.border_
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（含逆回购）'], column = 1+cell_index, value=round(self.dyzcjz_lh1_-6000000,2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（含逆回购） = 盈利/亏损（不含逆回购
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（含逆回购）'], column = 1+cell_index).border = self.border_
                            zhzcjz += self.dyzcjz_lh1_
                        else:
                            set_value(sheet, 6,1+cell_index,'单元资产净值(净价)', value, '量化一-单元资产', True, self.border_) # 单元资产净值 = 《单元资产》“单元资产净值(净价)”权益类一单元
                            tmp_dyzcjz = float(value['单元资产净值(净价)'])                        
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（含逆回购）'], column = 1+cell_index, value=round(tmp_dyzcjz-2400*10000,2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 #盈利/亏损（含逆回购）= 单元资产净值-2400万
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（含逆回购）'], column = 1+cell_index).border = self.border_
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（不含逆回购）'], column = 1+cell_index, value=hzzq_hegp_ztyk).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（不含逆回购） =《汇总证券（合计-股票）》“总体盈亏（含费用）”最后一行数值
                            sheet.cell(row = self.sheet_2_row_dict_['盈利/亏损（不含逆回购）'], column = 1+cell_index).border = self.border_
                            zhzcjz += tmp_dyzcjz
                            
                        cell_index += 1
                        cell_col_index[key] = cell_index   
                                    
                sheet.cell(row = self.sheet_2_row_dict_['账户资产净值'], column = 2, value=zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet_2_row_dict_['账户资产净值'], column = 2).border = self.border_
                sheet.cell(row = self.sheet_2_row_dict_['总盈利/亏损（含逆回购）'], column = 2, value=zhzcjz-3000*10000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet_2_row_dict_['总盈利/亏损（含逆回购）'], column = 2).border = self.border_
                
                zyk_bnhj = self.dyzcjz_lh1_-6000000 + hzzq_hegp_ztyk  # '=盈利/亏损（不含逆回购）这一行数据的和, '=单元资产净值-600万元 + 《汇总证券（合计-股票）》“总体盈亏（含费用）”最后一行数值
                sheet.cell(row = self.sheet_2_row_dict_['总盈利/亏损（不含逆回购）'], column = 2, value=zyk_bnhj).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet_2_row_dict_['总盈利/亏损（不含逆回购）'], column = 2).border = self.border_
                sheet.cell(row = self.sheet_2_row_dict_['收益率（不含逆回购）'], column = 2, value=str(round(zyk_bnhj/3000/10000*100, 4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet_2_row_dict_['收益率（不含逆回购）'], column = 2).border = self.border_
                
                value3 = (zhzcjz - 3000*10000) / 3000 / 10000 * 100 # 收益率（含逆回购）= 总盈利/亏损（含逆回购）÷3000万元×100%【保留4位小数】
                sheet.cell(row = self.sheet_2_row_dict_['收益率（含逆回购）'], column = 2, value = str(round(value3,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet_2_row_dict_['收益率（含逆回购）'], column = 2).border = self.border_
                cell_count = cell_index                
            else:
                logging.warning("量化一-单元资产文件不存在。")
            
            jyshg_profit = 0 # 交易所回购
            if self.src_excel_file_dict_['量化一']['交易所回购'] is not None:
                if 'profit' in self.src_excel_file_dict_['量化一']['交易所回购']:   
                    jyshg_profit = self.src_excel_file_dict_['量化一']['交易所回购']['profit']
                    sheet.cell(row = self.sheet_2_row_dict_['交易所回购'], column = cell_col_index['权益类一单元'], value = jyshg_profit).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_2_row_dict_['交易所回购'], column = cell_col_index['权益类一单元']).border = self.border_
                    
                    sheet.cell(row = self.sheet_2_row_dict_['交易所回购'], column = cell_col_index['量化一-投机单元'], value ='-')
                else:
                    logging.warning("量化一-交易所回购文件不存在。")
            else:
                logging.warning("量化一-交易所回购文件不存在。")            
                                
            if self.src_excel_file_dict_['量化一']['期货保证金分析'] is not None:
                for key, value in self.src_excel_file_dict_['量化一']['期货保证金分析'].items():
                    if key in cell_col_index:
                        set_value(sheet, self.sheet_2_row_dict_['占用'],cell_col_index[key],'占用保证金(静态)', value, '量化一-期货保证金分析', True)
                        sheet.cell(row = self.sheet_2_row_dict_['账户权益'], column = cell_col_index[key], value=self.dyzcjz_lh1_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 单元资产净值
                        sheet.cell(row = self.sheet_2_row_dict_['账户权益'], column = cell_col_index[key]).border = self.border_
                        risk_value = float(value['占用保证金(静态)']) / self.dyzcjz_lh1_ * 100 # 风险度 = 占用÷账户权益×100%【保留4位小数】
                        sheet.cell(row = self.sheet_2_row_dict_['风险度'], column = cell_col_index[key], value=str(round(risk_value,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 风险度 = 占用÷账户权益×100%【保留4位小数】
                        sheet.cell(row = self.sheet_2_row_dict_['风险度'], column = cell_col_index[key]).border = self.border_
                    else:
                        logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                
                sheet.cell(row = self.sheet_2_row_dict_['占用'], column = 3, value="-").border = self.border_
                sheet.cell(row = self.sheet_2_row_dict_['账户权益'], column = 3,value="-").border = self.border_
                sheet.cell(row = self.sheet_2_row_dict_['风险度'], column = 3,value="-").border = self.border_
            else:
                logging.warning("量化一-期货保证金分析文件不存在。")
            
            sszb = 3000*10000
            qcdwjz = sszb/self.total_amount1_ #期初单位净值
            dwjz = zhzcjz/self.total_amount1_ #单位净值
            
            sheet.cell(row = self.sheet_2_row_dict_['实收资本'], column = 2, value = sszb).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_2_row_dict_['资产净值'], column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_2_row_dict_['总份额'], column = 2, value = self.total_amount1_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_2_row_dict_['期初单位净值'], column = 2, value = round(qcdwjz, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_2_row_dict_['昨日单位净值'], column = 2, value = round(self.last_jz1_2_, 5))
            sheet.cell(row = self.sheet_2_row_dict_['单位净值'], column = 2, value = round(dwjz, 5))
            sheet.cell(row = self.sheet_2_row_dict_['日净值增长率'], column = 2, value = str(round((dwjz - self.last_jz1_2_)/self.last_jz1_2_*100, 5)) + '%')          
            
            self.new_jz_1_2_ = round(dwjz, 5)
            
            sheet.cell(row = self.sheet_2_row_dict_['实收资本'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_2_row_dict_['资产净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_2_row_dict_['总份额'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_2_row_dict_['期初单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_2_row_dict_['昨日单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_2_row_dict_['单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_2_row_dict_['日净值增长率'], column = 2).border = self.border_        
            
            if self.src_excel_file_dict_['量化一']['成交回报'] is not None:
                set_value(sheet, self.sheet_2_row_dict_['交易方向及数量'],2,'future_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
                set_value(sheet, self.sheet_2_row_dict_['交易方向及数量'],3,'stock_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
            else:
                logging.warning("量化一-成交回报文件不存在。")
                
            if self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet_2_row_dict_['持仓品种及数量'],2,'future_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
                set_value(sheet, self.sheet_2_row_dict_['持仓品种及数量'],3,'stock_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
            else:
                logging.warning("量化一-汇总证券-当日持仓文件不存在。")  
                
            extra_info = f"注:\n1、盈利/亏损（不含逆回购）数据暂未包含中金所申报费，盈利/亏损（含逆回购）数据已包含中金所申报费。"
            sheet.cell(row = self.sheet_2_row_dict_['注释'], column = 1, value = extra_info)                                 
            
            '''
            设置样式
            '''
            set_sheet_middle(sheet)

            sheet.column_dimensions['A'].width = 26
            # 设置第二列（B列）的宽度为10个字符
            sheet.column_dimensions['B'].width = 58
            # 设置第三列（C列）的宽度为15个字符
            sheet.column_dimensions['C'].width = 58        

            for key, value in self.sheet_2_row_dict_.items():
                if key == '交易方向及数量' or key == '持仓品种及数量':
                    sheet.row_dimensions[value].height = 140 
                elif key == '注释':
                    sheet.row_dimensions[value].height = 60
                else:
                    sheet.row_dimensions[value].height = 32
            
            sheet.cell(row = self.sheet_2_row_dict_['交易方向及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
            sheet.cell(row = self.sheet_2_row_dict_['交易方向及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
            sheet.cell(row = self.sheet_2_row_dict_['持仓品种及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
            sheet.cell(row = self.sheet_2_row_dict_['持仓品种及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            sheet.cell(row = self.sheet_2_row_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            
            for key, value in self.sheet_2_row_dict_.items():
                if '注释' in key or '、' in key:
                    sheet.merge_cells(start_row=value, start_column=1, end_row=value, end_column=cell_count)
                elif key in merge_col_list:
                    sheet.merge_cells(start_row=value, start_column=2, end_row=value, end_column=cell_count)    
                                                
                    
            self.all_jz_1_2_['date'].append(self.date)
            self.all_jz_1_2_['unit_net_value'].append(self.new_jz_1_2_)      
            self.all_jz_1_2_['hc_list'] = calc_max_drawdown(self.all_jz_1_2_['unit_net_value'],  self.all_jz_1_2_['hc_list'])  
            self.draw_save_pic(self.all_jz_1_2_, sheet, '量化一-结算数据')           
        except Exception as e:
            logging.error(f"生成 量化一-收盘数据 表格时发生错误: {e}")
               
    def gene_third_sheet(self):
        try:
            self.sheet_3_row_dict_ = {
                '统计日期':1,
                '一、账户资产及收益情况':2,
                '账户名称':3,
                '账户编号':4,
                '资产单元名称':5,
                '账户资产净值':6,
                '总盈利/亏损':7,
                '收益率':8,
                '二、净值列示':9,
                '实收资本':10,
                '资产净值':11,
                '总份额':12,
                '期初单位净值':13,
                '昨日单位净值':14,
                '单位净值':15,
                '日净值增长率':16,
                '三、保证金使用情况':17,
                '占用':18,
                '账户权益':19,
                '风险度':20,
                '四、交易情况':21,
                '交易方向及数量':22,
                '五、持仓情况':23,
                '持仓品种及数量':24
            }
                
            sheet = self.target_workbook_.create_sheet(title='量化二-结算数据')
            
            for key, value in self.sheet_3_row_dict_.items():
                if value is not None:
                    if key != '统计日期' and key != '注释':
                        sheet.cell(row = value, column = 1, value = key).font = self.font_
                        sheet.cell(row = value, column = 1, value = key).border = self.border_
                    else:
                        sheet.cell(row = value, column = 1, value = key)
                                    
            sheet.cell(row = self.sheet_3_row_dict_['一、账户资产及收益情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_3_row_dict_['二、净值列示'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_3_row_dict_['三、保证金使用情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_3_row_dict_['四、交易情况'], column = 1).fill = self.fill_        
            sheet.cell(row = self.sheet_3_row_dict_['五、持仓情况'], column = 1).fill = self.fill_
                            
        
            cell_count = 1             
            cell_col_index = {}
            zhzcjz = 0
            if self.src_excel_file_dict_['量化二']['单元资产'] is not None:
                cell_index = 1
                for key, value in self.src_excel_file_dict_['量化二']['单元资产'].items():
                    if key != '合计':
                        sheet.cell(row = self.sheet_3_row_dict_['统计日期'], column = 2, value=str(value['统计日期']) + ", （金额单位：元）").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        # sheet.cell(row = self.sheet_3_row_dict_['统计日期'], column = 2).border = self.border_
                        set_value(sheet, self.sheet_3_row_dict_['账户名称'],2,'账户名称', value, '量化二-单元资产', False,self.border_)
                        tmpzhbh = value['账户编号']
                        sheet.cell(row = self.sheet_3_row_dict_['账户编号'], column = 2, value=math.floor(float(tmpzhbh)))
                        sheet.cell(row = self.sheet_3_row_dict_['账户编号'], column = 2).border = self.border_
                        set_value(sheet, self.sheet_3_row_dict_['资产单元名称'],1+cell_index,'资产单元名称', value, '量化二-单元资产', False, self.border_)
                        set_value(sheet, self.sheet_3_row_dict_['账户资产净值'],1+cell_index,'单元资产净值(净价)', value, '量化二-单元资产', True, self.border_)
                        zhzcjz = float(value['单元资产净值(净价)'])
                        cell_index += 1
                        cell_col_index[key] = cell_index    
                # print(cell_col_index)
                cell_count = cell_index
        
            else:
                logging.warning("量化二-单元资产文件不存在。")
                    
            profits1 = 0  #总盈利/亏损（不含逆回购）
            if self.src_excel_file_dict_['量化二']['汇总证券-合计'] is not None:
                if 'profit' in self.src_excel_file_dict_['量化二']['汇总证券-合计']:
                    profits1 = self.src_excel_file_dict_['量化二']['汇总证券-合计']['profit']
                    sheet.cell(row = self.sheet_3_row_dict_['总盈利/亏损'], column = 2, value = round(zhzcjz - 1000*10000,4)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_3_row_dict_['总盈利/亏损'], column = 2).border = self.border_
                    value2 = profits1 / 1000 / 10000 * 100
                    value2 = round(value2, 4)
                    sheet.cell(row = self.sheet_3_row_dict_['收益率'], column = 2, value = str(value2)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_3_row_dict_['收益率'], column = 2).border = self.border_
                else:
                    logging.warning("量化二-汇总证券-合计文件不存在。")
            else:
                logging.warning("量化二-汇总证券-合计文件不存在。")
                    
                
            if self.src_excel_file_dict_['量化二']['期货保证金分析'] is not None:
                for key, value in self.src_excel_file_dict_['量化二']['期货保证金分析'].items():
                    if key in cell_col_index:
                        set_value(sheet, self.sheet_3_row_dict_['占用'],cell_col_index[key],'占用保证金(静态)', value, '量化二-期货保证金分析', True, self.border_)
                        set_value(sheet, self.sheet_3_row_dict_['账户权益'],cell_col_index[key],'账户权益', value, '量化二-期货保证金分析', True, self.border_)
                        sheet.cell(row = self.sheet_3_row_dict_['风险度'], column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet_3_row_dict_['风险度'], column = cell_col_index[key]).border = self.border_
                    else:
                        logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
            else:
                logging.warning("量化二-期货保证金分析文件不存在。")
            
            sszb = 1000*10000
            qcdwjz = sszb/self.total_amount2_ #期初单位净值
            dwjz = zhzcjz/self.total_amount2_ #单位净值
                    
            sheet.cell(row = self.sheet_3_row_dict_['实收资本'], column = 2, value = sszb).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_3_row_dict_['资产净值'], column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_3_row_dict_['总份额'], column = 2, value = self.total_amount2_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_3_row_dict_['期初单位净值'], column = 2, value = round(qcdwjz, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_3_row_dict_['昨日单位净值'], column = 2, value = round(self.jz2_1_, 5))
            sheet.cell(row = self.sheet_3_row_dict_['单位净值'], column = 2, value = round(dwjz, 5))
            sheet.cell(row = self.sheet_3_row_dict_['日净值增长率'], column = 2, value = str(round((dwjz - self.jz2_1_)/self.jz2_1_*100, 5)) + '%')  
            
            self.new_jz_2_1_ = round(dwjz, 5)              
        
            sheet.cell(row = self.sheet_3_row_dict_['实收资本'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_3_row_dict_['资产净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_3_row_dict_['总份额'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_3_row_dict_['期初单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_3_row_dict_['昨日单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_3_row_dict_['单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_3_row_dict_['日净值增长率'], column = 2).border = self.border_              
                
            if self.src_excel_file_dict_['量化二']['成交回报'] is not None:
                set_value(sheet, self.sheet_3_row_dict_['交易方向及数量'],2,'future_info_2', self.src_excel_file_dict_['量化二']['成交回报'], '量化二-成交回报', False, self.border_)
            else:
                logging.warning("量化二-成交回报文件不存在。")
                
            if self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet_3_row_dict_['持仓品种及数量'],2,'future_info_2', self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'], '量化二-汇总证券-当日持仓', False, self.border_)
            else:
                logging.warning("量化二-汇总证券-当日持仓文件不存在。")             
                                    
            # sheet.cell(row = self.sheet_3_row_dict_['注释'], column = 1, value = '注：交易情况中的商品期货数量未去重。')
                            
            set_sheet_middle(sheet)

            sheet.column_dimensions['A'].width = 26
            sheet.column_dimensions['B'].width = 58 

            for key, value in self.sheet_3_row_dict_.items():
                if key == '交易方向及数量' or key == '持仓品种及数量':
                    sheet.row_dimensions[value].height = 140 
                elif key == '注释':
                    sheet.row_dimensions[value].height = 60
                else:
                    sheet.row_dimensions[value].height = 27
            
            sheet.cell(row = self.sheet_3_row_dict_['交易方向及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
            sheet.cell(row = self.sheet_3_row_dict_['交易方向及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
            sheet.cell(row = self.sheet_3_row_dict_['持仓品种及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
            sheet.cell(row = self.sheet_3_row_dict_['持仓品种及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            # sheet.cell(row = self.sheet_3_row_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            
            for key, value in self.sheet_3_row_dict_.items():
                if '注释' in key or '、' in key:
                    sheet.merge_cells(start_row=value, start_column=1, end_row=value, end_column=cell_count)
                else:
                    sheet.merge_cells(start_row=value, start_column=2, end_row=value, end_column=cell_count)    
                
            self.all_jz_2_1_['date'].append(self.date)
            self.all_jz_2_1_['unit_net_value'].append(self.new_jz_2_1_)
            self.all_jz_2_1_['hc_list'] = calc_max_drawdown(self.all_jz_2_1_['unit_net_value'],self.all_jz_2_1_['hc_list']) 
            self.draw_save_pic(self.all_jz_2_1_, sheet, '量化二-收盘数据') 
        except Exception as e:
            logging.error(f"生成 量化二-结算数据 表格时发生错误: {e}")
                
    def gene_fourth_sheet(self):
        try:
            self.sheet_4_row_dict_ = {
                '统计日期':1,
                '一、账户资产及收益情况':2,
                '账户名称':3,
                '账户编号':4,
                '资产单元名称':5,
                '账户资产净值':6,
                '总盈利/亏损':7,
                '收益率':8,
                '二、净值列示':9,
                '实收资本':10,
                '资产净值':11,
                '总份额':12,
                '期初单位净值':13,
                '昨日单位净值':14,
                '单位净值':15,
                '日净值增长率':16,
                '三、保证金使用情况':17,
                '占用':18,
                '账户权益':19,
                '风险度':20,
                '四、交易情况':21,
                '交易方向及数量':22,
                '五、持仓情况':23,
                '持仓品种及数量':24
            }
                    
            sheet = self.target_workbook_.create_sheet(title='量化二-收盘数据')
            
            for key, value in self.sheet_4_row_dict_.items():
                if value is not None:
                    if key != '统计日期' and key != '注释':
                        sheet.cell(row = value, column = 1, value = key).font = self.font_
                        sheet.cell(row = value, column = 1, value = key).border = self.border_
                    else:
                        sheet.cell(row = value, column = 1, value = key)
                
            sheet.cell(row = self.sheet_4_row_dict_['一、账户资产及收益情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_4_row_dict_['二、净值列示'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_4_row_dict_['三、保证金使用情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_4_row_dict_['四、交易情况'], column = 1).fill = self.fill_        
            sheet.cell(row = self.sheet_4_row_dict_['五、持仓情况'], column = 1).fill = self.fill_
                    
            cell_count = 1             
            cell_col_index = {}
            zhzcjz = 0
            if self.src_excel_file_dict_['量化二']['单元资产'] is not None:
                cell_index = 1
                for key, value in self.src_excel_file_dict_['量化二']['单元资产'].items():
                    if key != '合计':
                        sheet.cell(row = self.sheet_4_row_dict_['统计日期'], column = 2, value=str(value['统计日期']) + ", （金额单位：元）")
                        set_value(sheet, self.sheet_4_row_dict_['账户名称'],2,'账户名称', value, '量化二-单元资产', False, self.border_)
                        tmpzhbh = value['账户编号']
                        sheet.cell(row = self.sheet_4_row_dict_['账户编号'], column = 2, value=math.floor(float(tmpzhbh)))
                        sheet.cell(row = self.sheet_4_row_dict_['账户编号'], column = 2).border = self.border_
                        set_value(sheet, self.sheet_4_row_dict_['资产单元名称'],1+cell_index,'资产单元名称', value, '量化二-单元资产', False, self.border_)
                        if '投机单元' not in key:
                            set_value(sheet, self.sheet_4_row_dict_['账户资产净值'],1+cell_index,'单元资产净值(净价)', value, '量化二-单元资产', False,self.border_)
                            zhzcjz = float(value['单元资产净值(净价)'])
                        else:
                            sheet.cell(row = self.sheet_4_row_dict_['账户资产净值'], column = 2, value=self.zhzcjz_lh2_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户资产净值 = 【手动输入】
                            sheet.cell(row = self.sheet_4_row_dict_['账户资产净值'], column = 2).border = self.border_
                            zhzcjz = self.zhzcjz_lh2_
                        
                        sheet.cell(row = self.sheet_4_row_dict_['总盈利/亏损'], column = 2, value=zhzcjz - 1000*10000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                        sheet.cell(row = self.sheet_4_row_dict_['总盈利/亏损'], column = 2).border = self.border_
                        value2 = (zhzcjz - 1000*10000) / 1000 / 10000 * 100 # 收益率 = （账户资产净值 - 1000万元）÷1000万元×100%【保留4位小数】
                        value2 = round(value2, 4)
                        sheet.cell(row = self.sheet_4_row_dict_['收益率'], column = 2, value = str(value2)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet_4_row_dict_['收益率'], column = 2).border = self.border_
                        
                        cell_index += 1
                        cell_col_index[key] = cell_index    
                # print(cell_col_index)
                cell_count = cell_index
        
            else:
                logging.warning("量化二-单元资产文件不存在。")
                    
        
            if self.src_excel_file_dict_['量化二']['期货保证金分析'] is not None:
                for key, value in self.src_excel_file_dict_['量化二']['期货保证金分析'].items():
                    if key in cell_col_index:   
                        sheet.cell(row = self.sheet_4_row_dict_['账户权益'], column = cell_col_index[key], value=self.zhzcjz_lh2_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 账户资产净值
                        sheet.cell(row = self.sheet_4_row_dict_['账户权益'], column = cell_col_index[key]).border = self.border_

                        zybzj = value['占用保证金(静态)']
                        sheet.cell(row = self.sheet_4_row_dict_['占用'], column = cell_col_index[key], value=zybzj).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 占用 = 手动输入
                        sheet.cell(row = self.sheet_4_row_dict_['占用'], column = cell_col_index[key]).border = self.border_

                        
                        fxd = round(zybzj/self.zhzcjz_lh2_*100, 4) # 风险度 = 占用÷账户权益×100%【保留4位小数】
                        sheet.cell(row = self.sheet_4_row_dict_['风险度'], column = cell_col_index[key], value= str(fxd)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 
                        sheet.cell(row = self.sheet_4_row_dict_['风险度'], column = cell_col_index[key]).border = self.border_
                    else:
                        logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
            else:
                logging.warning("量化二-期货保证金分析文件不存在。")
                
            sszb = 1000*10000
            qcdwjz = sszb/self.total_amount2_ #期初单位净值
            dwjz = zhzcjz/self.total_amount2_ #单位净值
            
        
        
            sheet.cell(row = self.sheet_4_row_dict_['实收资本'], column = 2, value = sszb).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_4_row_dict_['资产净值'], column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_4_row_dict_['总份额'], column = 2, value = self.total_amount2_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_4_row_dict_['期初单位净值'], column = 2, value = round(qcdwjz, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_4_row_dict_['昨日单位净值'], column = 2, value = round(self.jz2_2_, 5))
            sheet.cell(row = self.sheet_4_row_dict_['单位净值'], column = 2, value = round(dwjz, 5))
            sheet.cell(row = self.sheet_4_row_dict_['日净值增长率'], column = 2, value = str(round((dwjz - self.jz2_2_)/self.jz2_2_*100, 5)) + '%')  
            
            sheet.cell(row = self.sheet_4_row_dict_['实收资本'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_4_row_dict_['资产净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_4_row_dict_['总份额'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_4_row_dict_['期初单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_4_row_dict_['昨日单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_4_row_dict_['单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_4_row_dict_['日净值增长率'], column = 2).border = self.border_               
            
            self.new_jz_2_2_ = round(dwjz, 5)           
                
            if self.src_excel_file_dict_['量化二']['成交回报'] is not None:
                set_value(sheet, self.sheet_4_row_dict_['交易方向及数量'],2,'future_info_2', self.src_excel_file_dict_['量化二']['成交回报'], '量化二-成交回报',False,self.border_)
            else:
                logging.warning("量化二-成交回报文件不存在。")
                
            if self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet_4_row_dict_['持仓品种及数量'],2,'future_info_2', self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'], '量化二-汇总证券-当日持仓', False, self.border_)
            else:
                logging.warning("量化二-汇总证券-当日持仓文件不存在。")             
            # sheet.cell(row = self.sheet_4_row_dict_['注释'], column = 1, value = '注：交易情况中的商品期货数量未去重。')
            
    
            set_sheet_middle(sheet)

            sheet.column_dimensions['A'].width = 26
            # 设置第二列（B列）的宽度为10个字符
            sheet.column_dimensions['B'].width = 58     

            for key, value in self.sheet_4_row_dict_.items():
                if key == '交易方向及数量' or key == '持仓品种及数量':
                    sheet.row_dimensions[value].height = 140 
                elif key == '注释':
                    sheet.row_dimensions[value].height = 60
                else:
                    sheet.row_dimensions[value].height = 27
            
            sheet.cell(row = self.sheet_4_row_dict_['交易方向及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
            sheet.cell(row = self.sheet_4_row_dict_['交易方向及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
            sheet.cell(row = self.sheet_4_row_dict_['持仓品种及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
            sheet.cell(row = self.sheet_4_row_dict_['持仓品种及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            # sheet.cell(row = self.sheet_4_row_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                
            for key, value in self.sheet_4_row_dict_.items():
                if '注释' in key or '、' in key:
                    sheet.merge_cells(start_row=value, start_column=1, end_row=value, end_column=cell_count)
                else:
                    sheet.merge_cells(start_row=value, start_column=2, end_row=value, end_column=cell_count)        

            self.all_jz_2_2_['date'].append(self.date)
            self.all_jz_2_2_['unit_net_value'].append(self.new_jz_2_2_)
            self.all_jz_2_2_['hc_list'] = calc_max_drawdown(self.all_jz_2_2_['unit_net_value'], self.all_jz_2_2_['hc_list']) 
            self.draw_save_pic(self.all_jz_2_2_, sheet, '量化二-结算数据') 
        except Exception as e:
            logging.error(f"生成 量化二-收盘数据 表格时发生错误: {e}")

    def gene_fivth_sheet(self):
        try:
            self.sheet_5_row_dict_ = {
                '统计日期':1,
                '一、账户资产及收益情况':2,
                '账户名称':3,
                '账户编号':4,
                '资产单元名称':5,
                '账户资产净值':6,
                '总盈利/亏损':7,
                '收益率':8,
                '二、净值列示':9,
                '实收资本':10,
                '资产净值':11,
                '总份额':12,
                '期初单位净值':13,
                '昨日单位净值':14,
                '单位净值':15,
                '日净值增长率':16,
                '三、保证金使用情况':17,
                '占用':18,
                '账户权益':19,
                '风险度':20,
                '四、交易情况':21,
                '交易方向及数量':22,
                '五、持仓情况':23,
                '持仓品种及数量':24
            }
                
            sheet = self.target_workbook_.create_sheet(title='量化三-结算数据')
            
            for key, value in self.sheet_5_row_dict_.items():
                if value is not None:
                    if key != '统计日期' and key != '注释':
                        sheet.cell(row = value, column = 1, value = key).font = self.font_
                        sheet.cell(row = value, column = 1, value = key).border = self.border_
                    else:
                        sheet.cell(row = value, column = 1, value = key)
                                    
            sheet.cell(row = self.sheet_5_row_dict_['一、账户资产及收益情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_5_row_dict_['二、净值列示'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_5_row_dict_['三、保证金使用情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_5_row_dict_['四、交易情况'], column = 1).fill = self.fill_        
            sheet.cell(row = self.sheet_5_row_dict_['五、持仓情况'], column = 1).fill = self.fill_
                            
        
            cell_count = 1             
            cell_col_index = {}
            zhzcjz = 0
            if self.src_excel_file_dict_['量化三']['单元资产'] is not None:
                cell_index = 1
                for key, value in self.src_excel_file_dict_['量化三']['单元资产'].items():
                    if key != '合计':
                        sheet.cell(row = self.sheet_5_row_dict_['统计日期'], column = 2, value=str(value['统计日期']) + ", （金额单位：元）").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        # sheet.cell(row = self.sheet_5_row_dict_['统计日期'], column = 2).border = self.border_
                        set_value(sheet, self.sheet_5_row_dict_['账户名称'],2,'账户名称', value, '量化三-单元资产', False,self.border_)
                        tmpzhbh = value['账户编号']
                        sheet.cell(row = self.sheet_5_row_dict_['账户编号'], column = 2, value=math.floor(float(tmpzhbh)))
                        sheet.cell(row = self.sheet_5_row_dict_['账户编号'], column = 2).border = self.border_
                        set_value(sheet, self.sheet_5_row_dict_['资产单元名称'],1+cell_index,'资产单元名称', value, '量化三-单元资产', False, self.border_)
                        set_value(sheet, self.sheet_5_row_dict_['账户资产净值'],1+cell_index,'单元资产净值(净价)', value, '量化三-单元资产', True, self.border_)
                        zhzcjz = float(value['单元资产净值(净价)'])
                        cell_index += 1
                        cell_col_index[key] = cell_index    
                # print(cell_col_index)
                cell_count = cell_index
        
            else:
                logging.warning("量化三-单元资产文件不存在。")
                    
            profits1 = 0  #总盈利/亏损（不含逆回购）
            if self.src_excel_file_dict_['量化三']['汇总证券-合计'] is not None:
                if 'profit' in self.src_excel_file_dict_['量化三']['汇总证券-合计']:
                    profits1 = self.src_excel_file_dict_['量化三']['汇总证券-合计']['profit']
                    sheet.cell(row = self.sheet_5_row_dict_['总盈利/亏损'], column = 2, value = round(zhzcjz - 500*10000,4)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 与量化二不同的地方;
                    sheet.cell(row = self.sheet_5_row_dict_['总盈利/亏损'], column = 2).border = self.border_
                    value2 = profits1 / 1000 / 10000 * 100
                    value2 = round(value2, 4)
                    sheet.cell(row = self.sheet_5_row_dict_['收益率'], column = 2, value = str(value2)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet_5_row_dict_['收益率'], column = 2).border = self.border_
                else:
                    logging.warning("量化三-汇总证券-合计文件不存在。")
            else:
                logging.warning("量化三-汇总证券-合计文件不存在。")
                    
                
            if self.src_excel_file_dict_['量化三']['期货保证金分析'] is not None:
                for key, value in self.src_excel_file_dict_['量化三']['期货保证金分析'].items():
                    if key in cell_col_index:
                        set_value(sheet, self.sheet_5_row_dict_['占用'],cell_col_index[key],'占用保证金(静态)', value, '量化三-期货保证金分析', True, self.border_)
                        set_value(sheet, self.sheet_5_row_dict_['账户权益'],cell_col_index[key],'账户权益', value, '量化三-期货保证金分析', True, self.border_)
                        sheet.cell(row = self.sheet_5_row_dict_['风险度'], column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet_5_row_dict_['风险度'], column = cell_col_index[key]).border = self.border_
                    else:
                        logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
            else:
                logging.warning("量化三-期货保证金分析文件不存在。")
            
            sszb = 500*10000
            qcdwjz = sszb/self.total_amount3_ #期初单位净值
            dwjz = zhzcjz/self.total_amount3_ #单位净值
                    
            sheet.cell(row = self.sheet_5_row_dict_['实收资本'], column = 2, value = sszb).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_5_row_dict_['资产净值'], column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_5_row_dict_['总份额'], column = 2, value = self.total_amount3_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_5_row_dict_['期初单位净值'], column = 2, value = round(qcdwjz, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_5_row_dict_['昨日单位净值'], column = 2, value = round(self.jz3_1_, 5))
            sheet.cell(row = self.sheet_5_row_dict_['单位净值'], column = 2, value = round(dwjz, 5))
            sheet.cell(row = self.sheet_5_row_dict_['日净值增长率'], column = 2, value = str(round((dwjz - self.jz3_1_)/self.jz3_1_*100, 5)) + '%')  
            
            self.new_jz_3_1_ = round(dwjz, 5)              
        
            sheet.cell(row = self.sheet_5_row_dict_['实收资本'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_5_row_dict_['资产净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_5_row_dict_['总份额'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_5_row_dict_['期初单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_5_row_dict_['昨日单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_5_row_dict_['单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_5_row_dict_['日净值增长率'], column = 2).border = self.border_              
                
            if self.src_excel_file_dict_['量化三']['成交回报'] is not None:
                set_value(sheet, self.sheet_5_row_dict_['交易方向及数量'],2,'future_info', self.src_excel_file_dict_['量化三']['成交回报'], '量化三-成交回报', False, self.border_)  # 不同的地方
            else:
                logging.warning("量化三-成交回报文件不存在。")
                
            if self.src_excel_file_dict_['量化三']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet_5_row_dict_['持仓品种及数量'],2,'future_info', self.src_excel_file_dict_['量化三']['汇总证券-当日持仓'], '量化三-汇总证券-当日持仓', False, self.border_) # 不同的地方
            else:
                logging.warning("量化三-汇总证券-当日持仓文件不存在。")             
                                    
            # sheet.cell(row = self.sheet_5_row_dict_['注释'], column = 1, value = '注：交易情况中的商品期货数量未去重。')
                            
            set_sheet_middle(sheet)

            sheet.column_dimensions['A'].width = 26
            sheet.column_dimensions['B'].width = 58 

            for key, value in self.sheet_5_row_dict_.items():
                if key == '交易方向及数量' or key == '持仓品种及数量':
                    sheet.row_dimensions[value].height = 140 
                elif key == '注释':
                    sheet.row_dimensions[value].height = 60
                else:
                    sheet.row_dimensions[value].height = 27
            
            sheet.cell(row = self.sheet_5_row_dict_['交易方向及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
            sheet.cell(row = self.sheet_5_row_dict_['交易方向及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
            sheet.cell(row = self.sheet_5_row_dict_['持仓品种及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
            sheet.cell(row = self.sheet_5_row_dict_['持仓品种及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            # sheet.cell(row = self.sheet_5_row_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            
            for key, value in self.sheet_5_row_dict_.items():
                if '注释' in key or '、' in key:
                    sheet.merge_cells(start_row=value, start_column=1, end_row=value, end_column=cell_count)
                else:
                    sheet.merge_cells(start_row=value, start_column=2, end_row=value, end_column=cell_count)    
                
            self.all_jz_3_1_['date'].append(self.date)
            self.all_jz_3_1_['unit_net_value'].append(self.new_jz_3_1_)
            self.all_jz_3_1_['hc_list'] = calc_max_drawdown(self.all_jz_3_1_['unit_net_value'],self.all_jz_3_1_['hc_list']) 
            self.draw_save_pic(self.all_jz_3_1_, sheet, '量化三-结算数据') 

            # logging.info(self.all_jz_3_1_['unit_net_value'])

        except Exception as e:
            logging.error(f"生成 量化三-结算数据 表格时发生错误: {e}")
                
    def gene_sixth_sheet(self):
        try:
            self.sheet_6_row_dict_ = {
                '统计日期':1,
                '一、账户资产及收益情况':2,
                '账户名称':3,
                '账户编号':4,
                '资产单元名称':5,
                '账户资产净值':6,
                '总盈利/亏损':7,
                '收益率':8,
                '二、净值列示':9,
                '实收资本':10,
                '资产净值':11,
                '总份额':12,
                '期初单位净值':13,
                '昨日单位净值':14,
                '单位净值':15,
                '日净值增长率':16,
                '三、保证金使用情况':17,
                '占用':18,
                '账户权益':19,
                '风险度':20,
                '四、交易情况':21,
                '交易方向及数量':22,
                '五、持仓情况':23,
                '持仓品种及数量':24
            }
                    
            sheet = self.target_workbook_.create_sheet(title='量化三-收盘数据')
            
            for key, value in self.sheet_6_row_dict_.items():
                if value is not None:
                    if key != '统计日期' and key != '注释':
                        sheet.cell(row = value, column = 1, value = key).font = self.font_
                        sheet.cell(row = value, column = 1, value = key).border = self.border_
                    else:
                        sheet.cell(row = value, column = 1, value = key)
                
            sheet.cell(row = self.sheet_6_row_dict_['一、账户资产及收益情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_6_row_dict_['二、净值列示'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_6_row_dict_['三、保证金使用情况'], column = 1).fill = self.fill_
            sheet.cell(row = self.sheet_6_row_dict_['四、交易情况'], column = 1).fill = self.fill_        
            sheet.cell(row = self.sheet_6_row_dict_['五、持仓情况'], column = 1).fill = self.fill_
                    
            cell_count = 1             
            cell_col_index = {}
            zhzcjz = 0
            if self.src_excel_file_dict_['量化三']['单元资产'] is not None:
                cell_index = 1
                for key, value in self.src_excel_file_dict_['量化三']['单元资产'].items():
                    if key != '合计':
                        sheet.cell(row = self.sheet_6_row_dict_['统计日期'], column = 2, value=str(value['统计日期']) + ", （金额单位：元）")
                        set_value(sheet, self.sheet_6_row_dict_['账户名称'],2,'账户名称', value, '量化三-单元资产', False, self.border_)
                        tmpzhbh = value['账户编号']
                        sheet.cell(row = self.sheet_6_row_dict_['账户编号'], column = 2, value=math.floor(float(tmpzhbh)))
                        sheet.cell(row = self.sheet_6_row_dict_['账户编号'], column = 2).border = self.border_
                        set_value(sheet, self.sheet_6_row_dict_['资产单元名称'],1+cell_index,'资产单元名称', value, '量化三-单元资产', False, self.border_)
                        if '投机单元' not in key:
                            set_value(sheet, self.sheet_6_row_dict_['账户资产净值'],1+cell_index,'单元资产净值(净价)', value, '量化三-单元资产', False,self.border_)
                            zhzcjz = float(value['单元资产净值(净价)'])
                        else:
                            sheet.cell(row = self.sheet_6_row_dict_['账户资产净值'], column = 2, value=self.zhzcjz_lh3_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户资产净值 = 【手动输入】
                            sheet.cell(row = self.sheet_6_row_dict_['账户资产净值'], column = 2).border = self.border_
                            zhzcjz = self.zhzcjz_lh3_
                        
                        sheet.cell(row = self.sheet_6_row_dict_['总盈利/亏损'], column = 2, value=zhzcjz - 1000*10000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                        sheet.cell(row = self.sheet_6_row_dict_['总盈利/亏损'], column = 2).border = self.border_
                        value2 = (zhzcjz - 1000*10000) / 1000 / 10000 * 100 # 收益率 = （账户资产净值 - 1000万元）÷1000万元×100%【保留4位小数】
                        value2 = round(value2, 4)
                        sheet.cell(row = self.sheet_6_row_dict_['收益率'], column = 2, value = str(value2)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet_6_row_dict_['收益率'], column = 2).border = self.border_
                        
                        cell_index += 1
                        cell_col_index[key] = cell_index    
                # print(cell_col_index)
                cell_count = cell_index
        
            else:
                logging.warning("量化三-单元资产文件不存在。")
                    
        
            if self.src_excel_file_dict_['量化三']['期货保证金分析'] is not None:
                for key, value in self.src_excel_file_dict_['量化三']['期货保证金分析'].items():
                    if key in cell_col_index:   
                        sheet.cell(row = self.sheet_6_row_dict_['账户权益'], column = cell_col_index[key], value=self.zhzcjz_lh3_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 账户资产净值
                        sheet.cell(row = self.sheet_6_row_dict_['账户权益'], column = cell_col_index[key]).border = self.border_
                        
                        zybzj = value['占用保证金(静态)']

                        set_value(sheet, self.sheet_6_row_dict_['占用'],cell_col_index[key],'占用保证金(静态)', value, '量化三-期货保证金分析', True, self.border_)
                        sheet.cell(row = self.sheet_6_row_dict_['风险度'], column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet_6_row_dict_['风险度'], column = cell_col_index[key]).border = self.border_
                        
                        fxd = round(zybzj/self.zhzcjz_lh3_*100, 4) # 风险度 = 占用÷账户权益×100%【保留4位小数】
                        sheet.cell(row = self.sheet_6_row_dict_['风险度'], column = cell_col_index[key], value= str(fxd)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 
                        sheet.cell(row = self.sheet_6_row_dict_['风险度'], column = cell_col_index[key]).border = self.border_                        

                    else:
                        logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
            else:
                logging.warning("量化三-期货保证金分析文件不存在。")
                
            sszb = 1000*10000
            qcdwjz = sszb/self.total_amount3_ #期初单位净值
            dwjz = zhzcjz/self.total_amount3_ #单位净值
            
        
        
            sheet.cell(row = self.sheet_6_row_dict_['实收资本'], column = 2, value = sszb).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_6_row_dict_['资产净值'], column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_6_row_dict_['总份额'], column = 2, value = self.total_amount3_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_6_row_dict_['期初单位净值'], column = 2, value = round(qcdwjz, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = self.sheet_6_row_dict_['昨日单位净值'], column = 2, value = round(self.jz3_2_, 5))
            sheet.cell(row = self.sheet_6_row_dict_['单位净值'], column = 2, value = round(dwjz, 5))
            sheet.cell(row = self.sheet_6_row_dict_['日净值增长率'], column = 2, value = str(round((dwjz - self.jz3_2_)/self.jz3_2_*100, 5)) + '%')  
            
            sheet.cell(row = self.sheet_6_row_dict_['实收资本'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_6_row_dict_['资产净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_6_row_dict_['总份额'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_6_row_dict_['期初单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_6_row_dict_['昨日单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_6_row_dict_['单位净值'], column = 2).border = self.border_
            sheet.cell(row = self.sheet_6_row_dict_['日净值增长率'], column = 2).border = self.border_               
            
            self.new_jz_3_2_ = round(dwjz, 5)           
                
            if self.src_excel_file_dict_['量化三']['成交回报'] is not None:
                set_value(sheet, self.sheet_6_row_dict_['交易方向及数量'],2,'future_info', self.src_excel_file_dict_['量化三']['成交回报'], '量化三-成交回报',False,self.border_)
            else:
                logging.warning("量化三-成交回报文件不存在。")
                
            if self.src_excel_file_dict_['量化三']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet_6_row_dict_['持仓品种及数量'],2,'future_info', self.src_excel_file_dict_['量化三']['汇总证券-当日持仓'], '量化三-汇总证券-当日持仓', False, self.border_)
            else:
                logging.warning("量化三-汇总证券-当日持仓文件不存在。")             
            # sheet.cell(row = self.sheet_6_row_dict_['注释'], column = 1, value = '注：交易情况中的商品期货数量未去重。')
            
    
            set_sheet_middle(sheet)

            sheet.column_dimensions['A'].width = 26
            # 设置第二列（B列）的宽度为10个字符
            sheet.column_dimensions['B'].width = 58     

            for key, value in self.sheet_6_row_dict_.items():
                if key == '交易方向及数量' or key == '持仓品种及数量':
                    sheet.row_dimensions[value].height = 140 
                elif key == '注释':
                    sheet.row_dimensions[value].height = 60
                else:
                    sheet.row_dimensions[value].height = 27
            
            sheet.cell(row = self.sheet_6_row_dict_['交易方向及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
            sheet.cell(row = self.sheet_6_row_dict_['交易方向及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
            sheet.cell(row = self.sheet_6_row_dict_['持仓品种及数量'], column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
            sheet.cell(row = self.sheet_6_row_dict_['持仓品种及数量'], column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
            # sheet.cell(row = self.sheet_6_row_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                
            for key, value in self.sheet_6_row_dict_.items():
                if '注释' in key or '、' in key:
                    sheet.merge_cells(start_row=value, start_column=1, end_row=value, end_column=cell_count)
                else:
                    sheet.merge_cells(start_row=value, start_column=2, end_row=value, end_column=cell_count)        

            self.all_jz_3_2_['date'].append(self.date)
            self.all_jz_3_2_['unit_net_value'].append(self.new_jz_3_2_)
            self.all_jz_3_2_['hc_list'] = calc_max_drawdown(self.all_jz_3_2_['unit_net_value'], self.all_jz_3_2_['hc_list']) 
            logging.info(f"{self.all_jz_3_2_['hc_list']}")
            self.draw_save_pic(self.all_jz_3_2_, sheet, '量化三-收盘数据') 
            logging.info(f"{self.all_jz_3_2_['hc_list']}")
        except Exception as e:
            logging.error(f"生成 量化三-收盘数据 表格时发生错误: {e}")
               
if __name__ == "__main__":
    # create_excel_with_pandas()
    # create_excel_with_openpyxl()
    # test_dialog()
    # get_file_name()
    
    excelobj = ExcelBase()
    excelobj.Work()
    input("请输入任意字符后按回车键退出程序...")
    sys.exit()