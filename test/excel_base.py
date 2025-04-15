import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
from datetime import datetime
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side, colors
from openpyxl.styles import numbers
from openpyxl.chart import BarChart, Reference, Series
import xlrd
import sys
import json
import os
import logging
import math

logging.basicConfig(level = logging.INFO,  format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s', 
                    filename='运行日志.log',
                    filemode='w')

def get_file_name(file_path='./'):
    # 获取当前日期和时间
    now = datetime.now()
    # 将日期格式化为字符串，这里以常见的 '年-月-日' 格式为例
    date_str = now.strftime('%Y-%m-%d')   
    file_name = file_path + '/量化业务日报-' + date_str + '.xlsx'
    # logging.info(f"文件名：{file_name}")
    return file_name
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
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal='center', vertical='center')
def set_sheet_width_height(sheet):

    for col_num, column_cells in enumerate(sheet.columns, 1):
        max_length = 0
        column_letter = get_column_letter(col_num)
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        # logging.info(f"调整列宽 {column_letter} {adjusted_width}")
        sheet.column_dimensions[column_letter].width = adjusted_width
        
    for row_num, row in enumerate(sheet.iter_rows(), 1):
        max_height = 0
        for cell in row:
            try:
                lines = str(cell.value).count('\n') + 1
                cell_height = lines * 15  # 假设每行文本高度为15
                if cell_height > max_height:
                    max_height = cell_height
            except:
                pass
        # logging.info(f"调整行高 {row_num} {max_height}")
        sheet.row_dimensions[row_num].height = max_height    

def set_value(sheet, row, col, key, value, file_name, is_number = False, border = None):
    if key in value:
        if is_number:
            sheet.cell(row = row, column = col, value = float(value[key])).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
        else:
            sheet.cell(row = row, column = col, value = value[key])
            
        if border is not None:
            sheet.cell(row = row, column = col).border = border
    else:
        logging.warning(f"字段 {key} 不存在于文件{file_name}中。")
class ExcelDataRead():
    def __init__(self):
        pass
    
    def read_excel_sheet(self, xlrd_sheet, data_type): 
        try:
            if data_type == '单元资产':
                return self.read_dyzc_data(self=self , xlrd_sheet=xlrd_sheet)
            elif data_type == '汇总证券-合计':
                return self.read_hzzq_hj(self=self , xlrd_sheet=xlrd_sheet)   
            elif data_type == '交易所回购':
                return self.read_jyshg(self=self, xlrd_sheet=xlrd_sheet)   
            elif data_type == '期货保证金分析':
                return self.read_qhbzjfx(self=self, xlrd_sheet=xlrd_sheet) 
            elif data_type == '成交回报':
                return self.read_cjhb(self=self, xlrd_sheet=xlrd_sheet)    
            elif data_type == '汇总证券-当日持仓':
                return self.read_hzzq_drcc(self=self, xlrd_sheet=xlrd_sheet) 
            elif data_type == '汇总证券-合计-股票':
                return self.read_hzzz_hj_gp(self=self, xlrd_sheet=xlrd_sheet)                                          
            else:
                return None
        except Exception as e:
            logging.error(f"读取文件 {data_type} 时发生错误: {e}")  
        return None   
    
    def read_dyzc_data(self, xlrd_sheet):
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
            sys.exit(1)
        return None   
        
    def read_hzzq_hj(self, xlrd_sheet):
        try:
            cell_dict = {}
            logging.info(f"读取文件 汇总证券-合计 开始 {xlrd_sheet.nrows} {xlrd_sheet.ncols} ")
            for row in range(xlrd_sheet.nrows):
                for col in range(xlrd_sheet.ncols):
                    cell_value = str(xlrd_sheet.cell_value(row, col))
                    if row == xlrd_sheet.nrows - 1 and col == xlrd_sheet.ncols - 1:
                        # print(cell_value)
                        profit = float(cell_value)
                        profit = round(profit, 4)
            cell_dict['profit'] = profit
            
            # print(cell_dict)
            return cell_dict
        except Exception as e:
            logging.error(f"读取文件 单元资产 时发生错误: {e}")  
            sys.exit(1)
        return None                          

    def read_jyshg(self, xlrd_sheet):
        try:
            profit_col = -1
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                if '利润' == cell_value:
                    profit_col = col
                    
            if profit_col == -1:
                logging.critical("文件中未找到利润列，请检查。")
                sys.exit(1)
                            
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
            sys.exit(1)
        return None     
            
    def read_qhbzjfx(self, xlrd_sheet):
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
            sys.exit(1)
        return None     
                                              
    def read_cjhb(self, xlrd_sheet):
        try:
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
                        if stock_name not in future_list:
                            future_list.append(stock_name)
                    elif '期权' in value:
                        if stock_name not in option_list:
                            option_list.append(stock_name)
                                                
                    future_done_amount += cell_dict['成交金额'][row]
                                        
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
            future_info = f"今日交易: {len(future_list)} 只股指期货合约, {len(option_list)} 只股指期权合约， 成交金额 {round(future_done_amount,2)} 万元"
            
            future_info_2 = '今日交易'
            
            if len(future_list) > 0:
                future_info_2 += f" {len(future_list)} 只期货合约"
            if len(option_list) > 0:
                future_info_2 += f" {len(option_list)} 只期权合约"
            future_info_2 += f" 成交金额 {round(future_done_amount,2)} 万元"
            
            stock_info_2 = ''
            if stock_buy_count > 0:
                stock_info_2 += f"买入股票: {stock_buy_count} 只"
            if stock_sell_count > 0:
                stock_info_2 += f"卖出股票: {stock_sell_count} 只"
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
            sys.exit(1)
        return None     

    def read_hzzq_drcc(self, xlrd_sheet):
        try:
            cell_dict = {}            
            header_col_dict = {}
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                valid_item = ['持仓数量',  '证券代码', '持仓多空标志', '证券类别']                
                if cell_value in valid_item:
                    header_col_dict[cell_value] = col
                    cell_dict[cell_value] = []
                           
            for key, col in header_col_dict.items():
                for nrow in range(xlrd_sheet.nrows):
                    if nrow == 0:
                        continue
                    cell_value = str(xlrd_sheet.cell_value(nrow, col))                    
                    if key == '持仓数量':
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
                               
            for value in cell_dict['证券类别']:
                if '股票' in value:                    
                    if cell_dict['持仓数量'][row] > 0:
                        stock_count += 1
                elif '期货' in value or '期权' in value:
                    if '期货' in value and cell_dict['持仓数量'][row] > 0:
                        future_count += 1
                    elif '期权' in value and cell_dict['持仓数量'][row] > 0:
                        option_count += 1                        
                    
                    stock_name = cell_dict['证券代码'][row]                    
                    trade_type = cell_dict['持仓多空标志'][row]
                    
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
            # print(done_detail_dict)
                
            stock_info = f"股票: {stock_count} 只"            
            future_info = f"当前持有: {future_count} 只股指期货合约, {option_count} 只股指期权合约"
            
            if len(mckc) > 0 and mckc_count > 0:
                future_info += '\n权利仓: '
                for key, value in mckc.items():
                    if value > 0:
                        future_info += f"{key}({value} 手),"
                                                
            if len(mrkc) > 0 and mrkc_count > 0:
                future_info += '\n义务仓: '
                for key, value in mrkc.items():
                    if value > 0:
                        future_info += f"{key}({value} 手),"
                        
            if len(mcpc) > 0 and mcpc_count > 0:
                future_info += '\n多仓: '
                for key, value in mcpc.items():
                    if value > 0:
                        future_info += f"{key}({value} 手),"       
                        
            if len(mrpc) > 0 and mrpc_count > 0:
                future_info += '\n空仓: '
                for key, value in mrpc.items():
                    if value > 0:
                        future_info += f"{key}({value} 手),"             
            
            trade_detail_dict = {}
            trade_sum_dict = {}
            
            for stock_name, trade_dict in done_detail_dict.items():
                for trade_type, trade_count in trade_dict.items():
                    if trade_count > 0:                        
                        if trade_type not in trade_detail_dict:
                            trade_detail_dict[trade_type] = trade_count
                        else:
                            trade_detail_dict[trade_type] += trade_count
                            
                        if stock_name not in trade_sum_dict:
                            trade_sum_dict[stock_name] = trade_count
                                                                  
            result_dict = {}

            
            future_info_2 = f"共持仓 {len(trade_sum_dict)}只期货，其中"
            
            for key, value in trade_detail_dict.items():
                future_info_2 += f"{key}: {value} 只,"

            result_dict['stock_info'] = stock_info
            result_dict['future_info'] = future_info[0:len(future_info)-1]
            result_dict['future_info_2'] = future_info_2[0:len(future_info_2)-1]
            
            # print(result_dict)       
            return result_dict

        except Exception as e:
            logging.error(f"读取文件 汇总证券-当日持仓 时发生错误: {e}")  
            sys.exit(1)
        return None             

    def read_hzzz_hj_gp(self, xlrd_sheet):
        try:
            profit_col = -1
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                if '总体盈亏' in cell_value:
                    profit_col = col
                    
            if profit_col == -1:
                logging.critical("文件中未找到总体盈亏，请检查。")
                sys.exit(1)
                            
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
            sys.exit(1)
        return None     
        
class ExcelBase:
    def __init__(self):
        self.date = ''
        self.config_ = get_config()
        self.data_read_obj_ = ExcelDataRead
        if self.config_ is None:
            sys.exit(1)
        
        if '量化一二所在目录' not in self.config_:
            logging.critical("配置文件中未找到 '量化一二所在目录' 字段，请检查。")
            sys.exit(1)
            
        tmp_dir = self.config_['量化一二所在目录']         
        self.file_path_ = tmp_dir.replace('\\', '/')
        
        if os.path.exists(self.file_path_) == False:
            logging.critical(f"目录不存在，请检查。{self.file_path_}")
            sys.exit(1)
                    
        if '量化一-投机单元-单元资产净值' not in self.config_:
            logging.critical("配置文件中未找到 '量化一-投机单元-单元资产净值' 字段，请检查。")
            sys.exit(1)
            
        self.unit_net_value_ = float(str(self.config_['量化一-投机单元-单元资产净值'])) #手动输入的单元资产净值;
        if self.unit_net_value_ is None:
            logging.critical("配置文件中 '量化一-投机单元-单元资产净值' 字段值为空，请检查。")
            sys.exit(1)
            
        if '量化二-账户资产净值' not in self.config_:
            logging.critical("配置文件中未找到 '量化二-账户资产净值' 字段，请检查。")
            sys.exit(1)
            
        self.unit_net_value_2_ = float(str(self.config_['量化二-账户资产净值'])) #手动输入的单元资产净值;
        if self.unit_net_value_2_ is None:
            logging.critical("配置文件中 '量化二-账户资产净值' 字段值为空，请检查。")
            sys.exit(1)     
            
        if '量化二-占用' not in self.config_:
            logging.critical("配置文件中未找到 '量化二-占用' 字段，请检查。")
            sys.exit(1)
            
        self.unit_net_value_3_ = float(str(self.config_['量化二-占用'])) #手动输入的单元资产净值;
        if self.unit_net_value_3_ is None:
            logging.critical("配置文件中 '量化二-占用' 字段值为空，请检查。")
            sys.exit(1)                        
    
        
        # self.target_file_name_ = get_file_name(self.file_path_)
        # logging.info(f"目标文件名: {self.target_file_name_}")
        
        self.target_workbook_ = Workbook()
        
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
                '期货保证金分析':None
            },
            '量化二':{
                '成交回报':None,
                '单元资产':None,
                '汇总证券-当日持仓':None,
                '汇总证券-合计':None,
                '期货保证金分析':None
            }
        }
        
        self.src_excel_file_dict_ = self.init_excel_file(self.file_path_, self.src_excel_file_dict_)
        if self.src_excel_file_dict_ is None:
            logging.critical("初始化 Excel 文件失败。")
            sys.exit(1)          

    def init_excel_file(self, execl_file_path, file_dict):
        for key, value in file_dict.items():
            for key1, value1 in value.items():
                complete_file_path = execl_file_path + '/' + key + '/' + key1 + '.xls'        
                try:    
                    tmp_workbook = xlrd.open_workbook(complete_file_path)
                    tmp_sheet = tmp_workbook.sheet_by_index(0)
                    logging.info(f"成功读取文件 {complete_file_path}")
                    file_dict[key][key1] = self.data_read_obj_.read_excel_sheet(self=self.data_read_obj_, xlrd_sheet=tmp_sheet, data_type=key1)
                except FileNotFoundError:   
                    logging.error(f"文件 {complete_file_path} 未找到。")
                except Exception as e:
                    logging.error(f"读取文件 {complete_file_path} 时发生错误: {e}")                
        
        return file_dict            
                      
    def Work(self):
        self.gene_first_sheet()
        self.gene_second_sheet()
        self.gene_third_sheet()
        self.gene_fourth_sheet()
        
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
            
    def gene_first_sheet(self):
        sheet = self.target_workbook_.create_sheet(title='量化一-收盘数据')
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
        
        for key, value in self.src_excel_file_dict_['量化一'].items():
            if value is not None:
                if key != '统计日期':
                    sheet.cell(row = value, column = 1, value = key).border = self.border_
                    sheet.cell(row = value, column = 1, value = key).font = self.font_
                else:
                    sheet.cell(row = value, column = 1, value = key)
        
        sheet.cell(row = self.sheet_1_row_dict_['统计日期'], column = 3, value = "（金额单位：元）")
        
        # sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").font = self.font_
        sheet.cell(row = self.sheet_1_row_dict_['一、账户资产及收益情况'], column = 1).fill = self.fill_
        # sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").border = self.border_
        # sheet.cell(row = 3, column = 1, value = "账户名称").border = self.border_
        # sheet.cell(row = 3, column = 1, value = "账户名称").font = self.font_
        
        # sheet.cell(row = 4, column = 1, value = "账户编号").border = self.border_
        # sheet.cell(row = 4, column = 1, value = "账户编号").font = self.font_
        
        # sheet.cell(row = 5, column = 1, value = "资产单元名称").border = self.border_
        # sheet.cell(row = 5, column = 1, value = "资产单元名称").font = self.font_
        
        # sheet.cell(row = 6, column = 1, value = "单元资产净值").border = self.border_
        # sheet.cell(row = 6, column = 1, value = "单元资产净值").font = self.font_
        
        # sheet.cell(row = 7, column = 1, value = "账户资产净值").border = self.border_
        # sheet.cell(row = 7, column = 1, value = "账户资产净值").font = self.font_
        
        # sheet.cell(row = 8, column = 1, value = "交易所回购").border = self.border_
        # sheet.cell(row = 8, column = 1, value = "交易所回购").font = self.font_
        
        # sheet.cell(row = 9, column = 1, value = "总盈利/亏损（不含逆回购）").border = self.border_
        # sheet.cell(row = 9, column = 1, value = "总盈利/亏损（不含逆回购）").font = self.font_
        
        # sheet.cell(row = 10, column = 1, value = "收益率（不含逆回购）").border = self.border_
        # sheet.cell(row = 10, column = 1, value = "收益率（不含逆回购）").font = self.font_
        
        # sheet.cell(row = 11, column = 1, value = "总盈利/亏损（含逆回购）").border = self.border_
        # sheet.cell(row = 11, column = 1, value = "总盈利/亏损（含逆回购）").font = self.font_
        
        # sheet.cell(row = 12, column = 1, value = "收益率（含逆回购）").border = self.border_
        # sheet.cell(row = 12, column = 1, value = "收益率（含逆回购）").font = self.font_
        
        # sheet.cell(row = 13, column = 1, value = "二、保证金使用情况").border = self.border_
        # sheet.cell(row = 13, column = 1, value = "二、保证金使用情况").font = self.font_
        sheet.cell(row = self.sheet_1_row_dict_['三、保证金使用情况'], column = 1).fill = self.fill_
        
        # sheet.cell(row = 14, column = 1, value = "占用").border = self.border_
        # sheet.cell(row = 14, column = 1, value = "占用").font = self.font_
        
        # sheet.cell(row = 15, column = 1, value = "账户权益").border = self.border_  
        # sheet.cell(row = 15, column = 1, value = "账户权益").font = self.font_
        
        # sheet.cell(row = 16, column = 1, value = "风险度").border = self.border_       
        # sheet.cell(row = 16, column = 1, value = "风险度").font = self.font_
        
        # sheet.cell(row = 17, column = 1, value = "三、交易情况").border = self.border_  
        # sheet.cell(row = 17, column = 1, value = "三、交易情况").font = self.font_
        
        sheet.cell(row = self.sheet_1_row_dict_['四、交易情况'], column = 1).fill = self.fill_
        
        # sheet.cell(row = 18, column = 1, value = "交易方向及数量").border = self.border_  
        # sheet.cell(row = 18, column = 1, value = "交易方向及数量").font = self.font_
                
        # sheet.cell(row = 19, column = 1, value = "四、持仓情况").border = self.border_
        # sheet.cell(row = 19, column = 1, value = "四、持仓情况").font = self.font_
        
        sheet.cell(row = self.sheet_1_row_dict_['五、交易情况'], column = 1).fill = self.fill_
        
        # sheet.cell(row = 20, column = 1, value = "持仓品种及数量").border = self.border_   
        # sheet.cell(row = 20, column = 1, value = "持仓品种及数量").font = self.font_
        
        cell_count = 1             
        cell_col_index = {}
        zhzcjz = 0
        if self.src_excel_file_dict_['量化一']['单元资产'] is not None:
            cell_index = 1
            for key, value in self.src_excel_file_dict_['量化一']['单元资产'].items():
                if key != '合计':
                    set_value(sheet, 1,2,'统计日期', value, '量化一-单元资产',False, self.border_)
                    self.date = value['统计日期']
                    set_value(sheet, 3,2,'账户名称', value, '量化一-单元资产',False, self.border_)
                    tmpzhbh = value['账户编号']
                    sheet.cell(row = 4, column = 2, value=math.floor(float(tmpzhbh))).border = self.border_
                    set_value(sheet, 5,1+cell_index,'资产单元名称', value, '量化一-单元资产',False, self.border_)
                    set_value(sheet, 6,1+cell_index,'单元资产净值(净价)', value, '量化一-单元资产', True,self.border_)
                    cell_index += 1
                    cell_col_index[key] = cell_index    
                    
                    zhzcjz += float(value['单元资产净值(净价)'])                
                else :
                    set_value(sheet, 7,2,'单元资产净值(净价)', value, '量化一-单元资产',False, self.border_)
                    zhzcjz = float(value['单元资产净值(净价)'])
            # print(cell_col_index)
            cell_count = cell_index
            
            sheet.cell(row = 7, column = 2, value = zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = 7, column = 2).border = self.border_
            
            sheet.merge_cells(start_row=3, start_column=2, end_row=3, end_column=cell_count)
            sheet.merge_cells(start_row=4, start_column=2, end_row=4, end_column=cell_count)
                        
            sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=cell_count)
            sheet.merge_cells(start_row=7, start_column=2, end_row=7, end_column=cell_count)
            sheet.merge_cells(start_row=13, start_column=1, end_row=13, end_column=cell_count)
            sheet.merge_cells(start_row=17, start_column=1, end_row=17, end_column=cell_count)
            sheet.merge_cells(start_row=19, start_column=1, end_row=19, end_column=cell_count)
        else:
            logging.warning("量化一-单元资产文件不存在。")
            
        jyshg_profit = 0 # 交易所回购
        if self.src_excel_file_dict_['量化一']['交易所回购'] is not None:
            if 'profit' in self.src_excel_file_dict_['量化一']['交易所回购']:   
                jyshg_profit = self.src_excel_file_dict_['量化一']['交易所回购']['profit']
                sheet.cell(row = 8, column = cell_col_index['权益类一单元'], value =jyshg_profit).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = 8, column = cell_col_index['权益类一单元']).border = self.border_
            else:
                logging.warning("量化一-交易所回购文件不存在。")
        else:
            logging.warning("量化一-交易所回购文件不存在。")
        
        profits1 = 0  #总盈利/亏损（不含逆回购）
        if self.src_excel_file_dict_['量化一']['汇总证券-合计'] is not None:
            if 'profit' in self.src_excel_file_dict_['量化一']['汇总证券-合计']:
                profits1 = self.src_excel_file_dict_['量化一']['汇总证券-合计']['profit']
                sheet.cell(row = 9, column = 2, value = str(profits1)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = 9, column = 2).border = self.border_
                value2 = profits1 / 3000 / 10000 * 100
                value2 = round(value2, 4)
                sheet.cell(row = 10, column = 2, value = str(value2)+"%")
                sheet.cell(row = 10, column = 2).border = self.border_
                
                profits2 = zhzcjz - 30000000 #总盈利/亏损（含逆回购）
                profits2 = round(profits2, 2)
                sheet.cell(row = 11, column = 2, value = str(profits2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = 11, column = 2).border = self.border_
                value3 = profits2 / 3000 / 10000 * 100 # 收益率（含逆回购）
                value3 = round(value3, 4)
                sheet.cell(row = 12, column = 2, value = str(value3)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = 12, column = 2).border = self.border_
                
                sheet.merge_cells(start_row=9, start_column=2, end_row=9, end_column=cell_count)
                sheet.merge_cells(start_row=10, start_column=2, end_row=10, end_column=cell_count)
                sheet.merge_cells(start_row=11, start_column=2, end_row=11, end_column=cell_count)
                sheet.merge_cells(start_row=12, start_column=2, end_row=12, end_column=cell_count)
            else:
                logging.warning("量化一-汇总证券-合计文件不存在。")
        else:
            logging.warning("量化一-汇总证券-合计文件不存在。")
                
                
        if self.src_excel_file_dict_['量化一']['期货保证金分析'] is not None:
            for key, value in self.src_excel_file_dict_['量化一']['期货保证金分析'].items():
                if key in cell_col_index:
                    set_value(sheet, 14,cell_col_index[key],'占用保证金(静态)', value, '量化一-期货保证金分析',True, self.border_)
                    set_value(sheet, 15,cell_col_index[key],'账户权益', value, '量化一-期货保证金分析', True, self.border_)                    
                    sheet.cell(row = 16, column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),3))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = 16, column = cell_col_index[key]).border = self.border_
                else:
                    logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                    
            sheet.cell(row = 14, column = 3, value="-").border = self.border_
            sheet.cell(row = 15, column = 3,value="-").border = self.border_
            sheet.cell(row = 16, column = 3,value="-").border = self.border_
        else:
            logging.warning("量化一-期货保证金分析文件不存在。")
            
        if self.src_excel_file_dict_['量化一']['成交回报'] is not None:
            set_value(sheet, 18,2,'future_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
            set_value(sheet, 18,3,'stock_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
        else:
            logging.warning("量化一-成交回报文件不存在。")
            
        if self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'] is not None:
            set_value(sheet, 20,2,'future_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓',False, self.border_)
            set_value(sheet, 20,3,'stock_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
        else:
            logging.warning("量化一-汇总证券-当日持仓文件不存在。")             
        
        extra_info = f"注:\n1、总盈利/亏损(不含逆回购): 根据032盈亏数据计算,未扣除中金所申报费。\n"
        extra_info += f"2、总盈利/亏损（含逆回购）：已扣除中金所申报费；按照O32盈亏数据计算的未扣除申报费的金额为：{round(jyshg_profit + profits1,4)} 元。\n"
        sheet.cell(row = 21, column = 1, value = extra_info).border = self.border_
        sheet.merge_cells(start_row=21, start_column=1, end_row=21, end_column=cell_count)
        
   
        
        
        # extra_info = f"注:\n1、总盈利/亏损(不含逆回购): 根据032盈亏数据计算,未扣除中金所申报费。\n"
        # extra_info += f"2、总盈利/亏损（含逆回购）：已扣除中金所申报费；按照O32盈亏数据计算的未扣除申报费的金额为：{round(jyshg_profit + profits1,4)} 元。\n"
        # sheet.cell(row = 23, column = 1, value = extra_info)
        # sheet.merge_cells(start_row=21, start_column=1, end_row=21, end_column=cell_count)
                
        # set_sheet_width_height(sheet)
        set_sheet_middle(sheet)

        sheet.column_dimensions['A'].width = 26
        # 设置第二列（B列）的宽度为10个字符
        sheet.column_dimensions['B'].width = 58
        # 设置第三列（C列）的宽度为15个字符
        sheet.column_dimensions['C'].width = 58        
        sheet.row_dimensions[1].height = 27        
        sheet.row_dimensions[2].height = 27        
        sheet.row_dimensions[3].height = 27        
        sheet.row_dimensions[4].height = 27        
        sheet.row_dimensions[5].height = 27        
        sheet.row_dimensions[6].height = 27        
        sheet.row_dimensions[7].height = 27   
        
        sheet.row_dimensions[8].height = 27        
        sheet.row_dimensions[9].height = 27        
        sheet.row_dimensions[10].height = 27        
        sheet.row_dimensions[11].height = 27   
        sheet.row_dimensions[12].height = 27        
        sheet.row_dimensions[13].height = 27        
        sheet.row_dimensions[14].height = 27        
        sheet.row_dimensions[15].height = 27   
        sheet.row_dimensions[16].height = 27        
        sheet.row_dimensions[17].height = 27        
        sheet.row_dimensions[18].height = 140        
        sheet.row_dimensions[19].height = 27   
        sheet.row_dimensions[20].height = 140  
        sheet.row_dimensions[21].height = 60           
        
        sheet.cell(row = 18, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
        sheet.cell(row = 18, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
        sheet.cell(row = 20, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
        sheet.cell(row = 20, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
        sheet.cell(row = 21, column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)      
        
    def gene_second_sheet(self):
        sheet = self.target_workbook_.create_sheet(title='量化一-结算数据')
        self.sheet_2_row_dict_ = {
            '统计日期':1,
            '一、账户资产及收益情况':2,
            '账户名称':3,
            '账户编号':4,
            '资产单元名称':5,
            '单元资产净值':6,
            '账户资产净值':7,
            '交易所回购':8,
            '盈利/亏损（不含逆回购':9,
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
        for key, value in self.src_excel_file_dict_['量化一'].items():
            if value is not None:
                if key != '统计日期':
                    sheet.cell(row = value, column = 1, value = key).border = self.border_
                    sheet.cell(row = value, column = 1, value = key).font = self.font_
                else:
                    sheet.cell(row = value, column = 1, value = key)
                                    
        
        sheet.cell(row = 1, column = 1, value = "统计日期")
        
        sheet.cell(row = 1, column = 3, value = "（金额单位：元）")
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").border = self.border_
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").font = self.font_
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").fill = self.fill_
        
        sheet.cell(row = 3, column = 1, value = "账户名称").border = self.border_
        sheet.cell(row = 3, column = 1, value = "账户名称").font = self.font_
        
        sheet.cell(row = 4, column = 1, value = "账户编号").border = self.border_
        sheet.cell(row = 4, column = 1, value = "账户编号").font = self.font_
        
        
        sheet.cell(row = 5, column = 1, value = "资产单元名称").border = self.border_
        sheet.cell(row = 5, column = 1, value = "资产单元名称").font = self.font_
        
        sheet.cell(row = 6, column = 1, value = "单元资产净值").border = self.border_
        sheet.cell(row = 6, column = 1, value = "单元资产净值").font = self.font_
                        
        sheet.cell(row = 7, column = 1, value = "账户资产净值").border = self.border_
        sheet.cell(row = 7, column = 1, value = "账户资产净值").font = self.font_
        sheet.cell(row = 8, column = 1, value = "交易所回购").border = self.border_
        sheet.cell(row = 8, column = 1, value = "交易所回购").font = self.font_
        
        sheet.cell(row = 9, column = 1, value = "盈利/亏损（不含逆回购）").border = self.border_
        sheet.cell(row = 9, column = 1, value = "盈利/亏损（不含逆回购）").font = self.font_
        sheet.cell(row = 10, column = 1, value = "总盈利/亏损（不含逆回购）").border = self.border_
        sheet.cell(row = 10, column = 1, value = "总盈利/亏损（不含逆回购）").font = self.font_
        sheet.cell(row = 11, column = 1, value = "收益率（不含逆回购）").border = self.border_
        sheet.cell(row = 11, column = 1, value = "收益率（不含逆回购）").font = self.font_
        sheet.cell(row = 12, column = 1, value = "盈利/亏损（含逆回购）").border = self.border_
        sheet.cell(row = 12, column = 1, value = "盈利/亏损（含逆回购）").font = self.font_
        sheet.cell(row = 13, column = 1, value = "总盈利/亏损（含逆回购）").border = self.border_
        sheet.cell(row = 13, column = 1, value = "总盈利/亏损（含逆回购）").font = self.font_
        sheet.cell(row = 14, column = 1, value = "收益率（含逆回购）").border = self.border_
        sheet.cell(row = 14, column = 1, value = "收益率（含逆回购）").font = self.font_
         
        sheet.cell(row = 15, column = 1, value = "二、保证金使用情况").border = self.border_
        sheet.cell(row = 15, column = 1, value = "二、保证金使用情况").font = self.font_
        sheet.cell(row = 15, column = 1, value = "二、保证金使用情况").fill = self.fill_
        sheet.cell(row = 16, column = 1, value = "占用").border = self.border_
        sheet.cell(row = 16, column = 1, value = "占用").font = self.font_
        sheet.cell(row = 17, column = 1, value = "账户权益").border = self.border_
        sheet.cell(row = 17, column = 1, value = "账户权益").font = self.font_
        
        sheet.cell(row = 18, column = 1, value = "风险度").border = self.border_
        sheet.cell(row = 18, column = 1, value = "风险度").font = self.font_
        
        sheet.cell(row = 19, column = 1, value = "三、交易情况").border = self.border_
        sheet.cell(row = 19, column = 1, value = "三、交易情况").font = self.font_
        sheet.cell(row = 19, column = 1, value = "三、交易情况").fill = self.fill_
        sheet.cell(row = 20, column = 1, value = "交易方向及数量").border = self.border_
        sheet.cell(row = 20, column = 1, value = "交易方向及数量").font = self.font_
        sheet.cell(row = 21, column = 1, value = "四、持仓情况").border = self.border_
        sheet.cell(row = 21, column = 1, value = "四、持仓情况").font = self.font_
        sheet.cell(row = 21, column = 1, value = "四、持仓情况").fill = self.fill_
        sheet.cell(row = 22, column = 1, value = "持仓品种及数量").border = self.border_
        sheet.cell(row = 22, column = 1, value = "持仓品种及数量").font = self.font_
        
        
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
                    set_value(sheet, 1,2,'统计日期', value, '量化一-单元资产', False,self.border_)
                    set_value(sheet, 3,2,'账户名称', value, '量化一-单元资产', False,self.border_)
                    tmpzhbh = value['账户编号']
                    sheet.cell(row = 4, column = 2, value=math.floor(float(tmpzhbh))).border = self.border_
                    if '量化一-投机单元' in key:
                        sheet.cell(row = 6, column = 1+cell_index, value=self.unit_net_value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 单元资产净值 = 手动输入
                        sheet.cell(row = 6, column = 1+cell_index).border = self.border_
                        sheet.cell(row = 9, column = 1+cell_index, value=self.unit_net_value_-6000000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（不含逆回购） = 单元资产净值-600万元
                        sheet.cell(row = 9, column = 1+cell_index).border = self.border_
                    set_value(sheet, 4,2,'账户编号', value, '量化一-单元资产', False, self.border_)
                    set_value(sheet, 5,1+cell_index,'资产单元名称', value, '量化一-单元资产', False, self.border_)
                    if '量化一-投机单元' in key:
                        sheet.cell(row = 6, column = 1+cell_index, value=self.unit_net_value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 单元资产净值 = 手动输入
                        sheet.cell(row = 6, column = 1+cell_index).border = self.border_
                        sheet.cell(row = 9, column = 1+cell_index, value=self.unit_net_value_-6000000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（不含逆回购） = 单元资产净值-600万元
                        sheet.cell(row = 9, column = 1+cell_index).border = self.border_
                        sheet.cell(row = 12, column = 1+cell_index, value=round(self.unit_net_value_-6000000,2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（含逆回购） = 盈利/亏损（不含逆回购
                        sheet.cell(row = 12, column = 1+cell_index).border = self.border_
                        zhzcjz += self.unit_net_value_
                    else:
                        set_value(sheet, 6,1+cell_index,'单元资产净值(净价)', value, '量化一-单元资产', True, self.border_) # 单元资产净值 = 《单元资产》“单元资产净值(净价)”权益类一单元
                        tmp_dyzcjz = float(value['单元资产净值(净价)'])                        
                        sheet.cell(row = 12, column = 1+cell_index, value=round(tmp_dyzcjz-2400*10000,2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 #盈利/亏损（含逆回购）= 单元资产净值-2400万
                        sheet.cell(row = 12, column = 1+cell_index).border = self.border_
                        sheet.cell(row = 9, column = 1+cell_index, value=hzzq_hegp_ztyk).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损（不含逆回购） =《汇总证券（合计-股票）》“总体盈亏（含费用）”最后一行数值
                        sheet.cell(row = 9, column = 1+cell_index).border = self.border_
                        zhzcjz += tmp_dyzcjz
                        
                    cell_index += 1
                    cell_col_index[key] = cell_index   
                                
            sheet.cell(row = 7, column = 2, value=zhzcjz).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = 7, column = 2).border = self.border_
            sheet.cell(row = 13, column = 2, value=zhzcjz-3000*10000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = 13, column = 2).border = self.border_
            
            zyk_bnhj = self.unit_net_value_-6000000 + hzzq_hegp_ztyk  # '=盈利/亏损（不含逆回购）这一行数据的和, '=单元资产净值-600万元 + 《汇总证券（合计-股票）》“总体盈亏（含费用）”最后一行数值
            sheet.cell(row = 10, column = 2, value=zyk_bnhj).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = 10, column = 2).border = self.border_
            sheet.cell(row = 11, column = 2, value=str(round(zyk_bnhj/3000/10000*100, 4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = 11, column = 2).border = self.border_
            
            value3 = (zhzcjz - 3000*10000) / 3000 / 10000 * 100 # 收益率（含逆回购）= 总盈利/亏损（含逆回购）÷3000万元×100%【保留4位小数】
            sheet.cell(row = 14, column = 2, value = str(round(value3,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            sheet.cell(row = 14, column = 2).border = self.border_
            cell_count = cell_index
            
            sheet.merge_cells(start_row=3, start_column=2, end_row=3, end_column=cell_count)
            sheet.merge_cells(start_row=4, start_column=2, end_row=4, end_column=cell_count)
                        
            sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=cell_count)
            sheet.merge_cells(start_row=7, start_column=2, end_row=7, end_column=cell_count)
            sheet.merge_cells(start_row=10, start_column=2, end_row=10, end_column=cell_count)
            sheet.merge_cells(start_row=11, start_column=2, end_row=11, end_column=cell_count)
            sheet.merge_cells(start_row=13, start_column=2, end_row=13, end_column=cell_count)
            sheet.merge_cells(start_row=14, start_column=2, end_row=14, end_column=cell_count)
            sheet.merge_cells(start_row=15, start_column=1, end_row=15, end_column=cell_count)
            sheet.merge_cells(start_row=19, start_column=1, end_row=19, end_column=cell_count)
            sheet.merge_cells(start_row=21, start_column=1, end_row=21, end_column=cell_count)            
        else:
            logging.warning("量化一-单元资产文件不存在。")
            
        jyshg_profit = 0 # 交易所回购
        if self.src_excel_file_dict_['量化一']['交易所回购'] is not None:
            if 'profit' in self.src_excel_file_dict_['量化一']['交易所回购']:   
                jyshg_profit = self.src_excel_file_dict_['量化一']['交易所回购']['profit']
                sheet.cell(row = 8, column = cell_col_index['权益类一单元'], value = jyshg_profit).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = 8, column = cell_col_index['权益类一单元']).border = self.border_
            else:
                logging.warning("量化一-交易所回购文件不存在。")
        else:
            logging.warning("量化一-交易所回购文件不存在。")            
                                
        if self.src_excel_file_dict_['量化一']['期货保证金分析'] is not None:
            for key, value in self.src_excel_file_dict_['量化一']['期货保证金分析'].items():
                if key in cell_col_index:
                    set_value(sheet, 16,cell_col_index[key],'占用保证金(静态)', value, '量化一-期货保证金分析', True)
                    sheet.cell(row = 17, column = cell_col_index[key], value=self.unit_net_value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 单元资产净值
                    sheet.cell(row = 17, column = cell_col_index[key]).border = self.border_
                    risk_value = float(value['占用保证金(静态)']) / self.unit_net_value_ * 100 # 风险度 = 占用÷账户权益×100%【保留4位小数】
                    sheet.cell(row = 18, column = cell_col_index[key], value=str(round(risk_value,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 风险度 = 占用÷账户权益×100%【保留4位小数】
                    sheet.cell(row = 18, column = cell_col_index[key]).border = self.border_
                else:
                    logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
            
            sheet.cell(row = 16, column = 3, value="-").border = self.border_
            sheet.cell(row = 17, column = 3,value="-").border = self.border_
            sheet.cell(row = 18, column = 3,value="-").border = self.border_
        else:
            logging.warning("量化一-期货保证金分析文件不存在。")
            
        if self.src_excel_file_dict_['量化一']['成交回报'] is not None:
            set_value(sheet, 20,2,'future_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
            set_value(sheet, 20,3,'stock_info', self.src_excel_file_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
        else:
            logging.warning("量化一-成交回报文件不存在。")
            
        if self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'] is not None:
            set_value(sheet, 22,2,'future_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
            set_value(sheet, 22,3,'stock_info', self.src_excel_file_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
        else:
            logging.warning("量化一-汇总证券-当日持仓文件不存在。")  
            

        
        # set_sheet_width_height(sheet)
        set_sheet_middle(sheet)
        
        sheet.column_dimensions['A'].width = 26
        # 设置第二列（B列）的宽度为10个字符
        sheet.column_dimensions['B'].width = 58
        # 设置第三列（C列）的宽度为15个字符
        sheet.column_dimensions['C'].width = 58        
        sheet.row_dimensions[1].height = 27        
        sheet.row_dimensions[2].height = 27        
        sheet.row_dimensions[3].height = 27        
        sheet.row_dimensions[4].height = 27        
        sheet.row_dimensions[5].height = 27        
        sheet.row_dimensions[6].height = 27        
        sheet.row_dimensions[7].height = 27   
        
        sheet.row_dimensions[8].height = 27        
        sheet.row_dimensions[9].height = 27        
        sheet.row_dimensions[10].height = 27        
        sheet.row_dimensions[11].height = 27   
        sheet.row_dimensions[12].height = 27        
        sheet.row_dimensions[13].height = 27        
        sheet.row_dimensions[14].height = 27        
        sheet.row_dimensions[15].height = 27   
        sheet.row_dimensions[16].height = 27        
        sheet.row_dimensions[17].height = 27        
        sheet.row_dimensions[18].height = 27        
        sheet.row_dimensions[19].height = 27   
        sheet.row_dimensions[20].height = 140  
        sheet.row_dimensions[21].height = 27  
        sheet.row_dimensions[22].height = 140  
        
        sheet.cell(row = 20, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
        sheet.cell(row = 20, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
        sheet.cell(row = 22, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
        sheet.cell(row = 22, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)           
                
    def gene_third_sheet(self):
        self.sheet_1_row_dict_ = {
            '统计日期':1,
            '一、账户资产及收益情况':2,
            '账户名称':3,
            '账户编号':4,
            '资产单元名称':5,
            '账户资产净值':6,
            '交易所回购':7,
            '总盈利/亏损':8,
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
            '持仓品种及数量':24,
            '注释':25
        }
                
        sheet = self.target_workbook_.create_sheet(title='量化二-收盘数据')
        
        for key, value in self.src_excel_file_dict_['量化一'].items():
            if value is not None:
                if key != '统计日期':
                    sheet.cell(row = value, column = 1, value = key).border = self.border_
                    sheet.cell(row = value, column = 1, value = key).font = self.font_
                else:
                    sheet.cell(row = value, column = 1, value = key)
                            
        sheet.cell(row = 1, column = 1, value = "统计日期")
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").border = self.border_
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").font = self.font_
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").fill = self.fill_
        
        sheet.cell(row = 3, column = 1, value = "账户名称").border = self.border_
        sheet.cell(row = 3, column = 1, value = "账户名称").font = self.font_
        sheet.cell(row = 4, column = 1, value = "账户编号").border = self.border_
        sheet.cell(row = 4, column = 1, value = "账户编号").font = self.font_
        sheet.cell(row = 5, column = 1, value = "资产单元名称").border = self.border_
        sheet.cell(row = 5, column = 1, value = "资产单元名称").font = self.font_
        sheet.cell(row = 6, column = 1, value = "账户资产净值").border = self.border_
        sheet.cell(row = 6, column = 1, value = "账户资产净值").font = self.font_
        sheet.cell(row = 7, column = 1, value = "总盈利/亏损").border = self.border_
        sheet.cell(row = 7, column = 1, value = "总盈利/亏损").font = self.font_
        sheet.cell(row = 8, column = 1, value = "收益率").border = self.border_
        sheet.cell(row = 8, column = 1, value = "收益率").font = self.font_
        
        sheet.cell(row = 9, column = 1, value = "二、保证金使用情况").border = self.border_        
        sheet.cell(row = 9, column = 1, value = "二、保证金使用情况").font = self.font_
        sheet.cell(row = 9, column = 1, value = "二、保证金使用情况").fill = self.fill_
        
        sheet.cell(row = 10, column = 1, value = "占用").border = self.border_
        sheet.cell(row = 10, column = 1, value = "占用").font = self.font_
        sheet.cell(row = 11, column = 1, value = "账户权益").border = self.border_
        sheet.cell(row = 11, column = 1, value = "账户权益").font = self.font_
        sheet.cell(row = 12, column = 1, value = "风险度").border = self.border_
        sheet.cell(row = 12, column = 1, value = "风险度").font = self.font_
        sheet.cell(row = 13, column = 1, value = "三、交易情况").border = self.border_
        sheet.cell(row = 13, column = 1, value = "三、交易情况").font = self.font_
        sheet.cell(row = 13, column = 1, value = "三、交易情况").fill = self.fill_
        sheet.cell(row = 14, column = 1, value = "交易方向及数量").border = self.border_
        sheet.cell(row = 14, column = 1, value = "交易方向及数量").font = self.font_
        sheet.cell(row = 15, column = 1, value = "四、持仓情况").border = self.border_
        sheet.cell(row = 15, column = 1, value = "四、持仓情况").font = self.font_
        sheet.cell(row = 15, column = 1, value = "四、持仓情况").fill = self.fill_
        sheet.cell(row = 16, column = 1, value = "持仓品种及数量").border = self.border_
        sheet.cell(row = 16, column = 1, value = "持仓品种及数量").font = self.font_
        cell_count = 1             
        cell_col_index = {}
        zhzcjz = 0
        if self.src_excel_file_dict_['量化二']['单元资产'] is not None:
            cell_index = 1
            for key, value in self.src_excel_file_dict_['量化二']['单元资产'].items():
                if key != '合计':
                    sheet.cell(row = 1, column = 2, value=str(value['统计日期']) + ", （金额单位：元）").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = 1, column = 2).border = self.border_
                    set_value(sheet, 3,2,'账户名称', value, '量化二-单元资产', False,self.border_)
                    tmpzhbh = value['账户编号']
                    sheet.cell(row = 4, column = 2, value=math.floor(float(tmpzhbh)))
                    sheet.cell(row = 4, column = 2).border = self.border_
                    set_value(sheet, 5,1+cell_index,'资产单元名称', value, '量化二-单元资产', False, self.border_)
                    set_value(sheet, 6,1+cell_index,'单元资产净值(净价)', value, '量化二-单元资产', True, self.border_)
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
                sheet.cell(row = 7, column = 2, value = str(profits1)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = 7, column = 2).border = self.border_
                value2 = profits1 / 1000 / 10000 * 100
                value2 = round(value2, 4)
                sheet.cell(row = 8, column = 2, value = str(value2)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = 8, column = 2).border = self.border_
            else:
                logging.warning("量化二-汇总证券-合计文件不存在。")
        else:
            logging.warning("量化二-汇总证券-合计文件不存在。")
                
                
        if self.src_excel_file_dict_['量化二']['期货保证金分析'] is not None:
            for key, value in self.src_excel_file_dict_['量化二']['期货保证金分析'].items():
                if key in cell_col_index:
                    set_value(sheet, 10,cell_col_index[key],'占用保证金(静态)', value, '量化二-期货保证金分析', True, self.border_)
                    set_value(sheet, 11,cell_col_index[key],'账户权益', value, '量化二-期货保证金分析', True, self.border_)
                    # set_value(sheet, 12,cell_col_index[key],'风险比例1(%)', value, '量化二-期货保证金分析')
                    sheet.cell(row = 12, column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = 12, column = cell_col_index[key]).border = self.border_
                else:
                    logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
        else:
            logging.warning("量化二-期货保证金分析文件不存在。")
            
        if self.src_excel_file_dict_['量化二']['成交回报'] is not None:
            set_value(sheet, 14,2,'future_info_2', self.src_excel_file_dict_['量化二']['成交回报'], '量化二-成交回报', False, self.border_)
        else:
            logging.warning("量化二-成交回报文件不存在。")
            
        if self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'] is not None:
            set_value(sheet, 16,2,'future_info_2', self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'], '量化二-汇总证券-当日持仓', False, self.border_)
        else:
            logging.warning("量化二-汇总证券-当日持仓文件不存在。")             
        
   
        sheet.merge_cells(start_row=3, start_column=2, end_row=3, end_column=cell_count)
        sheet.merge_cells(start_row=4, start_column=2, end_row=4, end_column=cell_count)
        
        sheet.merge_cells(start_row=10, start_column=2, end_row=10, end_column=cell_count)
        sheet.merge_cells(start_row=11, start_column=2, end_row=11, end_column=cell_count)
        sheet.merge_cells(start_row=12, start_column=2, end_row=12, end_column=cell_count)
                                
        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=cell_count)
        sheet.merge_cells(start_row=9, start_column=1, end_row=9, end_column=cell_count)
        sheet.merge_cells(start_row=13, start_column=1, end_row=13, end_column=cell_count)
        sheet.merge_cells(start_row=15, start_column=1, end_row=15, end_column=cell_count)
        sheet.merge_cells(start_row=14, start_column=2, end_row=14, end_column=cell_count)
        sheet.merge_cells(start_row=16, start_column=2, end_row=16, end_column=cell_count)
                    
        
        sheet.cell(row = 17, column = 1, value = '注：交易情况中的商品期货数量未去重。')
        sheet.cell(row = 17, column = 1).border = self.border_
        sheet.cell(row = 17, column = 1).font = self.font_
        sheet.merge_cells(start_row=17, start_column=1, end_row=17, end_column=cell_count)
                
        # set_sheet_width_height(sheet)
        set_sheet_middle(sheet)
        sheet.column_dimensions['A'].width = 26
        # 设置第二列（B列）的宽度为10个字符
        sheet.column_dimensions['B'].width = 58
      
        sheet.row_dimensions[1].height = 27        
        sheet.row_dimensions[2].height = 27        
        sheet.row_dimensions[3].height = 27        
        sheet.row_dimensions[4].height = 27        
        sheet.row_dimensions[5].height = 27        
        sheet.row_dimensions[6].height = 27        
        sheet.row_dimensions[7].height = 27   
        
        sheet.row_dimensions[8].height = 27        
        sheet.row_dimensions[9].height = 27        
        sheet.row_dimensions[10].height = 27        
        sheet.row_dimensions[11].height = 27   
        sheet.row_dimensions[12].height = 27        
        sheet.row_dimensions[13].height = 27        
        sheet.row_dimensions[14].height = 140        
        sheet.row_dimensions[15].height = 27   
        sheet.row_dimensions[16].height = 140
        sheet.row_dimensions[17].height = 35
        
        sheet.cell(row = 14, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                   
        sheet.cell(row = 16, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
        sheet.cell(row = 17, column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
    
    def gene_fourth_sheet(self):
        self.sheet_1_row_dict_ = {
            '统计日期':1,
            '一、账户资产及收益情况':2,
            '账户名称':3,
            '账户编号':4,
            '资产单元名称':5,
            '账户资产净值':6,
            '交易所回购':7,
            '总盈利/亏损':8,
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
            '持仓品种及数量':24,
            '注释':25
        }
                
        sheet = self.target_workbook_.create_sheet(title='量化二-结算数据')
        
        for key, value in self.src_excel_file_dict_['量化一'].items():
            if value is not None:
                if key != '统计日期':
                    sheet.cell(row = value, column = 1, value = key).border = self.border_
                    sheet.cell(row = value, column = 1, value = key).font = self.font_
                else:
                    sheet.cell(row = value, column = 1, value = key)
                            
        sheet.cell(row = 1, column = 1, value = "统计日期")
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").border = self.border_
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").font = self.font_
        sheet.cell(row = 2, column = 1, value = "一、账户资产及收益情况").fill = self.fill_
        
        sheet.cell(row = 3, column = 1, value = "账户名称").border = self.border_
        sheet.cell(row = 3, column = 1, value = "账户名称").font = self.font_
        sheet.cell(row = 4, column = 1, value = "账户编号").border = self.border_
        sheet.cell(row = 4, column = 1, value = "账户编号").font = self.font_
        sheet.cell(row = 5, column = 1, value = "资产单元名称").border = self.border_
        sheet.cell(row = 5, column = 1, value = "资产单元名称").font = self.font_
        sheet.cell(row = 6, column = 1, value = "账户资产净值").border = self.border_
        sheet.cell(row = 6, column = 1, value = "账户资产净值").font = self.font_
        sheet.cell(row = 7, column = 1, value = "总盈利/亏损").border = self.border_
        sheet.cell(row = 7, column = 1, value = "总盈利/亏损").font = self.font_
        sheet.cell(row = 8, column = 1, value = "收益率").border = self.border_
        sheet.cell(row = 8, column = 1, value = "收益率").font = self.font_
        
        sheet.cell(row = 9, column = 1, value = "二、保证金使用情况").border = self.border_
        sheet.cell(row = 9, column = 1, value = "二、保证金使用情况").font = self.font_
        sheet.cell(row = 9, column = 1, value = "二、保证金使用情况").fill = self.fill_  
        sheet.cell(row = 10, column = 1, value = "占用").border = self.border_
        sheet.cell(row = 10, column = 1, value = "占用").font = self.font_
        sheet.cell(row = 11, column = 1, value = "账户权益").border = self.border_
        sheet.cell(row = 11, column = 1, value = "账户权益").font = self.font_  
        sheet.cell(row = 12, column = 1, value = "风险度").border = self.border_
        sheet.cell(row = 12, column = 1, value = "风险度").font = self.font_
        
        sheet.cell(row = 13, column = 1, value = "三、交易情况").border = self.border_
        sheet.cell(row = 13, column = 1, value = "三、交易情况").font = self.font_
        sheet.cell(row = 13, column = 1, value = "三、交易情况").fill = self.fill_
        sheet.cell(row = 14, column = 1, value = "交易方向及数量").border = self.border_
        sheet.cell(row = 14, column = 1, value = "交易方向及数量").font = self.font_
        
        
        sheet.cell(row = 15, column = 1, value = "四、持仓情况").border = self.border_
        sheet.cell(row = 15, column = 1, value = "四、持仓情况").font = self.font_
        sheet.cell(row = 15, column = 1, value = "四、持仓情况").fill = self.fill_
        sheet.cell(row = 16, column = 1, value = "持仓品种及数量").border = self.border_
        sheet.cell(row = 16, column = 1, value = "持仓品种及数量").font = self.font_
                
        cell_count = 1             
        cell_col_index = {}
        zhzcjz = 0
        if self.src_excel_file_dict_['量化二']['单元资产'] is not None:
            cell_index = 1
            for key, value in self.src_excel_file_dict_['量化二']['单元资产'].items():
                if key != '合计':
                    sheet.cell(row = 1, column = 2, value=str(value['统计日期']) + ", （金额单位：元）").border = self.border_
                    set_value(sheet, 3,2,'账户名称', value, '量化二-单元资产', False, self.border_)
                    tmpzhbh = value['账户编号']
                    sheet.cell(row = 4, column = 2, value=math.floor(float(tmpzhbh)))
                    sheet.cell(row = 4, column = 2).border = self.border_
                    set_value(sheet, 5,1+cell_index,'资产单元名称', value, '量化二-单元资产', False, self.border_)
                    if '投机单元' not in key:
                        set_value(sheet, 6,1+cell_index,'单元资产净值(净价)', value, '量化二-单元资产', False,self.border_)
                        zhzcjz = float(value['单元资产净值(净价)'])
                    else:
                        sheet.cell(row = 6, column = 2, value=self.unit_net_value_2_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户资产净值 = 【手动输入】
                        sheet.cell(row = 6, column = 2).border = self.border_
                        zhzcjz = self.unit_net_value_2_
                    
                    sheet.cell(row = 7, column = 2, value=zhzcjz - 1000*10000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                    sheet.cell(row = 7, column = 2).border = self.border_
                    value2 = (zhzcjz - 1000*10000) / 1000 / 10000 * 100 # 收益率 = （账户资产净值 - 1000万元）÷1000万元×100%【保留4位小数】
                    value2 = round(value2, 4)
                    sheet.cell(row = 8, column = 2, value = str(value2)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = 8, column = 2).border = self.border_
                    
                    cell_index += 1
                    cell_col_index[key] = cell_index    
            # print(cell_col_index)
            cell_count = cell_index
    
        else:
            logging.warning("量化二-单元资产文件不存在。")
                    
        
        if self.src_excel_file_dict_['量化二']['期货保证金分析'] is not None:
            for key, value in self.src_excel_file_dict_['量化二']['期货保证金分析'].items():
                if key in cell_col_index:   
                    sheet.cell(row = 10, column = cell_col_index[key], value=self.unit_net_value_3_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 占用 = 手动输入
                    sheet.cell(row = 10, column = cell_col_index[key]).border = self.border_
                    sheet.cell(row = 11, column = cell_col_index[key], value=self.unit_net_value_2_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 账户资产净值
                    sheet.cell(row = 11, column = cell_col_index[key]).border = self.border_
                    
                    value4 = round(self.unit_net_value_3_/self.unit_net_value_2_*100, 4) # 风险度 = 占用÷账户权益×100%【保留4位小数】
                    sheet.cell(row = 12, column = cell_col_index[key], value= str(value4)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 
                    sheet.cell(row = 12, column = cell_col_index[key]).border = self.border_
                else:
                    logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
        else:
            logging.warning("量化二-期货保证金分析文件不存在。")
            
        if self.src_excel_file_dict_['量化二']['成交回报'] is not None:
            set_value(sheet, 14,2,'future_info_2', self.src_excel_file_dict_['量化二']['成交回报'], '量化二-成交回报',False,self.border_)
        else:
            logging.warning("量化二-成交回报文件不存在。")
            
        if self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'] is not None:
            set_value(sheet, 16,2,'future_info_2', self.src_excel_file_dict_['量化二']['汇总证券-当日持仓'], '量化二-汇总证券-当日持仓', False, self.border_)
        else:
            logging.warning("量化二-汇总证券-当日持仓文件不存在。")             
        
   
        sheet.merge_cells(start_row=3, start_column=2, end_row=3, end_column=cell_count)
        sheet.merge_cells(start_row=4, start_column=2, end_row=4, end_column=cell_count)
        
        sheet.merge_cells(start_row=10, start_column=2, end_row=10, end_column=cell_count)
        sheet.merge_cells(start_row=11, start_column=2, end_row=11, end_column=cell_count)
        sheet.merge_cells(start_row=12, start_column=2, end_row=12, end_column=cell_count)
                                
        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=cell_count)
        sheet.merge_cells(start_row=9, start_column=1, end_row=9, end_column=cell_count)
        sheet.merge_cells(start_row=13, start_column=1, end_row=13, end_column=cell_count)
        sheet.merge_cells(start_row=15, start_column=1, end_row=15, end_column=cell_count)
        sheet.merge_cells(start_row=14, start_column=2, end_row=14, end_column=cell_count)
        sheet.merge_cells(start_row=16, start_column=2, end_row=16, end_column=cell_count)
                    
        
        sheet.cell(row = 17, column = 1, value = '注：交易情况中的商品期货数量未去重。')
        sheet.cell(row = 17, column = 1).border = self.border_
        sheet.cell(row = 17, column = 1).font = self.font_
        sheet.merge_cells(start_row=17, start_column=1, end_row=17, end_column=cell_count)
                
        # set_sheet_width_height(sheet)
        set_sheet_middle(sheet)
        
        # set_sheet_width_height(sheet)
        set_sheet_middle(sheet)
        sheet.column_dimensions['A'].width = 26
        # 设置第二列（B列）的宽度为10个字符
        sheet.column_dimensions['B'].width = 58
      
        sheet.row_dimensions[1].height = 27        
        sheet.row_dimensions[2].height = 27        
        sheet.row_dimensions[3].height = 27        
        sheet.row_dimensions[4].height = 27        
        sheet.row_dimensions[5].height = 27        
        sheet.row_dimensions[6].height = 27        
        sheet.row_dimensions[7].height = 27   
        
        sheet.row_dimensions[8].height = 27        
        sheet.row_dimensions[9].height = 27        
        sheet.row_dimensions[10].height = 27        
        sheet.row_dimensions[11].height = 27   
        sheet.row_dimensions[12].height = 27        
        sheet.row_dimensions[13].height = 27        
        sheet.row_dimensions[14].height = 140        
        sheet.row_dimensions[15].height = 27   
        sheet.row_dimensions[16].height = 140  
        sheet.row_dimensions[17].height = 35      
        
        sheet.cell(row = 14, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                   
        sheet.cell(row = 16, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)  
        sheet.cell(row = 17, column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)        

    
if __name__ == "__main__":
    # create_excel_with_pandas()
    # create_excel_with_openpyxl()
    # test_dialog()
    # get_file_name()
    
    excelobj = ExcelBase()
    excelobj.Work()
    input("请输入任意字符后按回车键退出程序...")
    sys.exit()