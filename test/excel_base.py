import pandas as pd
from openpyxl import Workbook
from openpyxl import load_workbook
from datetime import datetime
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side, Color
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

from pathlib import Path

def get_current_directory_os():
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    return current_directory

def get_current_directory_pathlib():
    current_directory = Path(__file__).parent.absolute()
    return current_directory

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

def check_system():
    if sys.platform.startswith('win'):
        return 'Windows'
    elif sys.platform.startswith('linux'):
        return 'Linux'
    else:
        return '其他系统'
    
def is_merge_all(key):
    if '注释' in key or '一' in key or '二' in key or '三' in key or '四' in key or '五' in key or '六' in key or '七' in key or '八' in key or '九' in key or '十' in key:
        return True
    else:
        return False    
    
def get_config():
    try:
        cur_dir = get_current_directory_os()
        if check_system() == 'Windows':
            config_file_path = cur_dir + '\\配置.json'
        else:   
            config_file_path = cur_dir + '/配置.json'
        logging.info(f"配置文件路径: {config_file_path}")
        config_file = open(config_file_path, 'r', encoding='utf-8')
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


def reset_date(date_list):
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

def draw_and_save_chart(draw_line_days, date_list,jz_list, hc_list, pic_name, label_info):
    try:            
        new_date_list = reset_date(date_list)
                
        max_hc = 0
        min_hc = min(hc_list)
        
        if min_hc == 0:
            min_hc = -0.05
            max_hc = 0
        
        max_net_value = max(jz_list)
        min_net_value = min(jz_list)
        
        delta = max_net_value - min_net_value
                    
        # print(new_date)
        plt.figure(figsize=(10, 6)) 
        
                
        df = pd.DataFrame({
            'date': new_date_list,
            'net_value': jz_list,
            'drawdown': hc_list
        })
        
        index_list, date_list = get_resize_index(new_date_list, 6)

        # 绘图设置
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # 绘制策略净值曲线
        color = 'tab:blue'
        ax1.set_xlabel('日期')
        ax1.set_ylabel('净值', color=color)
        ax1.plot(df['date'], df['net_value'], label='净值', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(ymin=min_net_value-delta*0.1, ymax=max_net_value+delta*0.1)
        ax1.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        

        # 创建第二个y轴用于绘制回撤
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('回撤', color=color)
            
            
        if len(hc_list) < draw_line_days:
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
        ax2.xaxis.set_major_locator(FixedLocator(index_list))
        # 设置刻度标签
        ax2.xaxis.set_major_formatter(FixedFormatter(date_list))              
        ax2.yaxis.set_major_formatter(PercentFormatter(1))

        # 添加标题和图例
        plt.title(label_info)
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, 0.93))

        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(pic_name)          
        plt.close() 
        return True                            
    except Exception as e:
        logging.error(f"绘制 {pic_name} 图时发生错误: {e}")   
        return False
     
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
            info = f'{index}.{type_name}:'
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
    def __init__(self, excel_base_data, industry_dict):
        self.excel_src_dict_ = excel_base_data
        self.excel_industry_dict_ = industry_dict
        # logging.info(self.excel_industry_dict_)

        # pass
    
    def calc_qusuo_value(self, long_dict, short_dict):
        try:
            rst = 0

            long_short_stock = []
            suocang_info = ''
            for stock, cc_info in long_dict.items():
                if stock in short_dict:
                    if cc_info['count'] != short_dict[stock]['count']:
                        tmp_amount = 0
                        if cc_info['count'] > short_dict[stock]['count']:
                            tmp_amount += (long_dict[stock]['count'] - short_dict[stock]['count']) * (long_dict[stock]['amount'] / long_dict[stock]['count'])
                        else:
                            tmp_amount += (short_dict[stock]['count'] - long_dict[stock]['count']) * (short_dict[stock]['amount'] / short_dict[stock]['count'])
                        rst += tmp_amount
                        logging.info(f"{stock}, long: {long_dict[stock]['amount']}, {long_dict[stock]['count']}; short: {short_dict[stock]['amount']}, {short_dict[stock]['count']}, 锁仓后市值: {tmp_amount}")
                        
                        suocang_info += f"{stock}, 多仓: {long_dict[stock]['amount']}, {long_dict[stock]['count']}; 空仓: {short_dict[stock]['amount']}, {short_dict[stock]['count']}, 锁仓后市值: {tmp_amount}\n"

                    long_short_stock.append(stock)
                else:
                    rst += cc_info['amount']

            self.excel_industry_dict_['合计']['统计数据']['标的列表信息'] = suocang_info
            for stock, cc_info in short_dict.items():
                if stock not in long_short_stock:
                    rst += cc_info['amount']
            
            return rst

        except Exception as e:
            logging.error(f"计算去锁市值失败, \nLong: {long_dict},\nShort: 1{short_dict},\n{e}")  
            return -1   
        
    def update_industry_static_data(self, stock_name, amount, is_long):
        try:
            not_other = False
            tmp_long = 0
            tmp_short = 0

            des_industry_name = '其他'
            des_object_name = '其他'

            for industry_name in self.excel_industry_dict_.keys():
                industry_detail = self.excel_industry_dict_[industry_name]
                if industry_name == '其他' or industry_name == '合计':
                    continue
                detail_array = industry_detail['标的详情']
                for object in detail_array:
                    if object in stock_name:
                        des_industry_name = industry_name
                        des_object_name = object
                        
                        if stock_name not in industry_detail['统计数据']['标的列表']:
                            if len(industry_detail['统计数据']['标的列表']) == 0:
                                industry_detail['统计数据']['标的列表信息'] = stock_name
                            else:
                                industry_detail['统计数据']['标的列表信息'] += ', ' + stock_name
                            
                            industry_detail['统计数据']['标的列表'].append(stock_name)
                            
                        not_other = True
                        if is_long:
                            industry_detail['统计数据']['多头市值'] += amount
                            tmp_long = amount
                        else:
                            industry_detail['统计数据']['空头市值'] += amount
                            tmp_short = amount
                        
                        industry_detail['统计数据']['净市值'] = industry_detail['统计数据']['多头市值'] - industry_detail['统计数据']['空头市值']
            
            # logging.info(f"${stock_name} ${des_industry_name} ${des_object_name}")
            # if '苹果2510' == stock_name:
                
            if not not_other:
                if stock_name not in self.excel_industry_dict_['其他']['统计数据']['标的列表']:
                    if len(self.excel_industry_dict_['其他']['统计数据']['标的列表']) == 0:
                        self.excel_industry_dict_['其他']['统计数据']['标的列表信息'] = stock_name
                    else:
                        self.excel_industry_dict_['其他']['统计数据']['标的列表信息'] += ', ' + stock_name
                    self.excel_industry_dict_['其他']['统计数据']['标的列表'].append(stock_name)                
                    
                if is_long:
                    self.excel_industry_dict_['其他']['统计数据']['多头市值'] += amount
                    tmp_long = amount
                else:
                    self.excel_industry_dict_['其他']['统计数据']['空头市值'] += amount  
                    tmp_short = amount

                self.excel_industry_dict_['其他']['统计数据']['净市值'] = self.excel_industry_dict_['其他']['统计数据']['多头市值'] - self.excel_industry_dict_['其他']['统计数据']['空头市值']

            self.excel_industry_dict_['合计']['统计数据']['多头市值'] += tmp_long
            self.excel_industry_dict_['合计']['统计数据']['空头市值'] += tmp_short
            self.excel_industry_dict_['合计']['统计数据']['净市值'] += tmp_long - tmp_short

        except Exception as e:
            logging.error(f"更新量化二行业统计信息出错, {stock_name}, {amount}, {is_long}: {e}")  
            return None     
            
    def read_excel_sheet(self, xlrd_sheet, data_type, sheet_type='量化一'): 
        try:
            if data_type == '单元资产':
                return self.read_dyzc_data(xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)
            elif data_type == '汇总证券-合计':
                return self.read_hzzq_hj(xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)   
            elif data_type == '交易所回购':
                return self.read_jyshg(xlrd_sheet=xlrd_sheet,sheet_type=sheet_type)   
            elif data_type == '期货保证金分析':
                return self.read_qhbzjfx(xlrd_sheet=xlrd_sheet,sheet_type=sheet_type) 
            elif data_type == '成交回报':
                return self.read_cjhb(xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)    
            elif data_type == '汇总证券-当日持仓':
                return self.read_hzzq_drcc( xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)  
            elif data_type == '汇总证券-合计-股票':
                return self.read_hzzz_hj_gp(xlrd_sheet=xlrd_sheet, sheet_type=sheet_type)                                          
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
                    
            # if '量化三' in sheet_type:
            #     logging.info(f"读取文件 单元资产 结束 {cell_dict} ")

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
                
            
            result_dict['future_info'] = future_info[0:len(future_info)-1]
                   
            return result_dict

        except Exception as e:
            logging.error(f"读取文件 量化三 成交回报 时发生错误: {e}")  
            
        return None    
    
    def read_cjhb(self, xlrd_sheet, sheet_type="量化一"):
        try:

            if sheet_type == "量化三":
                return self.read_cjhb_lhs(xlrd_sheet)

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
            result_dict['future_info'] = future_info[0:len(future_info)-1]
            
            # print(result_dict)       
            return result_dict

        except Exception as e:
            logging.error(f"读取文件 量化三 汇总证券-当日持仓 时发生错误: {e}")  
            
        return None             

    def read_hzzq_drcc(self, xlrd_sheet, sheet_type="量化一"):
        try:
            if sheet_type == "量化三":
                return self.read_hzzq_drcc_lhs(xlrd_sheet)
            cell_dict = {}            
            header_col_dict = {}
            for col in range(xlrd_sheet.ncols):
                cell_value = str(xlrd_sheet.cell_value(0, col))
                valid_item = ['持仓数量',  '证券代码', '证券名称','持仓多空标志', '证券类别','本币市值']              
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
                elif ('期货' in value or '期权' in value) and float(cell_dict['持仓数量'][row]) > 0.001:
                    if '期货' in value and cell_dict['持仓数量'][row] > 0:
                        future_count += 1
                    elif '期权' in value and cell_dict['持仓数量'][row] > 0:
                        option_count += 1                        

                    done_amount += cell_dict['本币市值'][row]
                    
                    stock_name = cell_dict['证券代码'][row]                    
                    trade_type = cell_dict['持仓多空标志'][row]

                    stock_detail_name = cell_dict['证券名称'][row]
                    
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
                        
                        if sheet_type  == "量化二":
                            self.update_industry_static_data(stock_name = stock_detail_name, amount=float(cell_dict['本币市值'][row])/10000, is_long=True)

                        if stock_name not in mcpc:
                            mcpc[stock_name] = {}
                            mcpc[stock_name]['count'] = cell_dict['持仓数量'][row]
                            mcpc[stock_name]['amount'] = cell_dict['本币市值'][row]
                        else:
                            mcpc[stock_name]['count']  += cell_dict['持仓数量'][row]
                            mcpc[stock_name]['amount'] += cell_dict['本币市值'][row]
                        mcpc_count += cell_dict['持仓数量'][row]
                    elif '空仓' in cell_dict['持仓多空标志'][row]:  
                        if sheet_type  == "量化二":
                            self.update_industry_static_data(stock_name = stock_detail_name, amount=float(cell_dict['本币市值'][row]/10000), is_long=False)
                        if stock_name not in mrpc:
                            mrpc[stock_name] = {}
                            mrpc[stock_name]['count'] = cell_dict['持仓数量'][row]
                            mrpc[stock_name]['amount'] = cell_dict['本币市值'][row]
                        else:
                            mrpc[stock_name]['count'] += cell_dict['持仓数量'][row]
                            mrpc[stock_name]['amount'] += cell_dict['本币市值'][row]
                        mrpc_count += cell_dict['持仓数量'][row]
                                                                    
                    
                    
                row += 1

            done_amount /= 10000
            # print(done_detail_dict)

            if sheet_type  == "量化二":
                self.excel_src_dict_['量化二']['其余信息']['结算数据']['总市值'] = round(done_amount,2) 
                self.excel_src_dict_['量化二']['其余信息']['结算数据']['去锁市值'] = round( self.calc_qusuo_value(mcpc, mrpc),  2)
                
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
                    if value['count'] > 0:
                        future_info += f"{key}({math.floor(float(value['count'] ))} 手),"       
                        
            if len(mrpc) > 0 and mrpc_count > 0:
                future_info += '\n空仓: '
                for key, value in mrpc.items():
                    if value['count']  > 0:
                        future_info += f"{key}({math.floor(float(value['count'] ))} 手),"             
            
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
    
def trans_hc_str(src_data):
    tmp_data = src_data
    if tmp_data.find('%') >= 0:                    
        new_s = tmp_data.replace('%', '')
        tmp_data = float(new_s)/100    
    else:
        tmp_data = float(tmp_data)
    return tmp_data

class JZData:
    def __init__(self, meta_info):
        self.jz_list_no_profit_ = []  # 净值序列-无返息    
        self.hc_list_no_profit_ = [] # 回撤序列-无返息    
        self.last_jz_no_profit_ = -1 # 昨日净值-无返息
        
        self.jz_list_with_profit_ = []  # 净值序列-有返息    
        self.hc_list_with_profit_ = [] # 回撤序列-有返息    
        self.last_jz_with_profit_ = -1 # 昨日净值-有返息        
        
        
        self.date_list_ = [] # 日期序列
        self.max_drawdown_ = -1 # 最大回撤
        self.max_drawdown_date_ = '' # 最大回撤日期
        self.meta_info_ = meta_info
        
    def read_data_from_excel_sheet(self, sheet, sheet_name):
        try:
            valid_row = get_last_row(sheet, sheet_name)
            
            # logging.info(f"读取文件 {sheet_name} 开始 {valid_row}")
            
            for i in range(2, valid_row+1):
                date = str(sheet.cell(row=i, column=1).value)
                
                jz_with_profit = float(sheet.cell(row=i, column=2).value)                
                hc_with_profit = trans_hc_str(str(sheet.cell(row=i, column=3).value))

                jz_no_profit = float(sheet.cell(row=i, column=4).value)
                hc_no_profit = trans_hc_str(str(sheet.cell(row=i, column=5).value))
                
                self.date_list_.append(date)
                self.jz_list_no_profit_.append(jz_no_profit)
                self.jz_list_with_profit_.append(jz_with_profit)
                self.hc_list_no_profit_.append(hc_no_profit)
                self.hc_list_with_profit_.append(hc_with_profit)
                            
            self.last_jz_no_profit_ = self.jz_list_no_profit_[-1]
            self.last_jz_with_profit_ = self.jz_list_with_profit_[-1]            
                
        except Exception as e:
            logging.error(f"读取文件 净值 发生错误: {e}")  
            return None
        
    
    def update_data(self, new_date, new_jz_with_profit, new_jz_no_profit):
        try:
            self.date_list_.append(new_date)
            self.jz_list_no_profit_.append(new_jz_no_profit)
            self.jz_list_with_profit_.append(new_jz_with_profit)
            
            self.hc_list_no_profit_ = calc_max_drawdown(self.jz_list_no_profit_, self.hc_list_no_profit_)
            self.hc_list_with_profit_ = calc_max_drawdown(self.jz_list_with_profit_, self.hc_list_with_profit_)
            
        except Exception as e:
            logging.error(f"{self.meta_info_}更新净值数据出错: {e}")  
            
    def draw_chart(self, draw_line_days, file_path, draw_net_value_curve, sheet, pic_name:str):
        try:            
            if draw_net_value_curve == 0:
                return
            # 绘制折线图
                                      
            pic_file_with_profit_name = file_path + '/' + pic_name + '_含返息.png'
            meta_info = '策略净值与回撤-含返息、手续费  ' + self.date_list_[-1]
            if '量化一' in pic_name:
                meta_info = '策略净值与回撤-含返息、手续费、逆回购 ' + self.date_list_[-1]
            if False == draw_and_save_chart(draw_line_days, self.date_list_, self.jz_list_with_profit_, self.hc_list_with_profit_, pic_file_with_profit_name, meta_info):
                return                                            
            img = Image(pic_file_with_profit_name)
            img.anchor = 'E2'
            sheet.add_image(img)
            

            pic_file_no_profit_name = file_path + '/' + pic_name + '_不含返息.png'
            meta_info = '策略净值与回撤-不含返息、手续费  ' + self.date_list_[-1]
            if '量化一' in pic_name:
                meta_info = '策略净值与回撤-不含返息、手续费、逆回购 ' + self.date_list_[-1]      
            if False == draw_and_save_chart(draw_line_days,self.date_list_, self.jz_list_no_profit_, self.hc_list_no_profit_, pic_file_no_profit_name, meta_info):
                return
            img = Image(pic_file_no_profit_name)
            img.anchor = 'E20'
            sheet.add_image(img)  
                            
        except Exception as e:
            logging.error(f"绘制 {pic_name} 图时发生错误: {e}")          
            
class ExcelData:
    def __init__(self, row=-1):
        self.row_ = row
        self.value_ = None
        self.is_merge_= False
       
def read_json_array(json_array, meta_info):
    try:
        result = []
        for data in json_array:
            result.append(data)
        return result
    except Exception as e:
        logging.error(f"读取${meta_info}信息出错: {e}")  
        return None   
             
def init_excel_file(execl_file_path, file_dict, data_read_obj:ExcelDataRead):
    try:
        for key, value in file_dict.items():
            tmp_dir = execl_file_path + '/' + key
            if os.path.exists(tmp_dir) == True:                                 
                for file_name, value1 in value.items():                    
                        if file_name != '其余信息' and file_name != '手动输入数据':
                            complete_file_path = execl_file_path + '/' + key + '/' + file_name + '.xls'  
                            if os.path.exists(complete_file_path) == True:
                                try:    
                                    tmp_workbook = xlrd.open_workbook(complete_file_path)
                                    tmp_sheet = tmp_workbook.sheet_by_index(0)
                                    logging.info(f"成功读取文件 {complete_file_path}")
                                    # file_dict = data_read_obj.read_excel_sheet(self=data_read_obj, xlrd_sheet=tmp_sheet, data_type=file_name, sheet_type=key)

                                    file_dict[key][file_name] = data_read_obj.read_excel_sheet(tmp_sheet, file_name, key)

                                except FileNotFoundError:   
                                    logging.warning(f"文件 {complete_file_path} 未找到。")
                                except Exception as e:
                                    logging.warning(f"读取文件 {complete_file_path} 时发生错误: {e}")       
                            else:
                                logging.warning(f"文件 {complete_file_path} 未找到。")
            else:
                file_dict[key]['其余信息']['isOpen'] = False
                logging.warning(f"目录 {tmp_dir} 未找到。")
                                    
    except Exception as e:
        logging.error(f"初始化 Excel 文件出错: {e}")  
        return None

def copy_sheet(src_sheet, des_sheet):
    try:
    # 遍历源sheet的每一行
        for row in src_sheet.iter_rows():
            new_row = []
            # 遍历当前行的每一个单元格
            for cell in row:
                # 将单元格的值和样式复制到新的单元格
                new_cell = des_sheet.cell(row=cell.row, column=cell.column, value=cell.value)
                if cell.has_style:
                    new_cell.font = cell.font.copy()
                    new_cell.border = cell.border.copy()
                    new_cell.fill = cell.fill.copy()
                    new_cell.number_format = cell.number_format
                    # new_cell.protection = cell.protection
                    new_cell.alignment = cell.alignment.copy()

                    # new_cell.font = cell.font
                    # new_cell.border = cell.border
                    # new_cell.fill = cell.fill
                    # new_cell.number_format = cell.number_format
                    # # new_cell.protection = cell.protection
                    # new_cell.alignment = cell.alignment                    
            # des_sheet.append(new_row)
    except Exception as e:
        logging.error(f"拷贝sheet 出错 {e}")  
        return None  

class ExcelBase:
    def __init__(self):
        try:
            
            self.date = ''
            self.config_ = get_config()
            
            self.industry_list_ = ['农副', '有色', '能化', '黑色', '贵金属', '股指期货', '其他', '合计']
            self.industry_dict_ = {}

            if self.config_ is None:
                logging.critical("配置文件为空，请检查。")
                return None
                            
            if '量化导出文件所在目录' not in self.config_:
                logging.critical("配置文件中未找到 '量化导出文件所在目录' 字段，请检查。")
                return None
                
                
            tmp_dir = self.config_['量化导出文件所在目录']         
            self.file_path_ = tmp_dir.replace('\\', '/')
            
            if os.path.exists(self.file_path_) == False:
                logging.critical(f"目录不存在，请检查。{self.file_path_}")
                return None
                                
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
            self.bold_font_ = Font(bold = True, size=14)
            self.no_bold_font_ = Font(size=14)        
            self.thin_border_ = Side(border_style='thin', color='000000')
            self.border_ = Border(left=self.thin_border_, right=self.thin_border_, top=self.thin_border_, bottom=self.thin_border_)
            
            self.with_profit_color_ = PatternFill(start_color='E4DFEC', end_color='E4DFEC', fill_type='solid')
            self.no_profit_color_ = PatternFill(start_color='DAEEF3', end_color='DAEEF3', fill_type='solid')

            self.sheet1_dict_ = {}
            self.sheet2_dict_ = {}
            self.sheet3_dict_ = {}
            self.sheet4_dict_ = {}
            self.sheet5_dict_ = {}
            self.sheet6_dict_ = {}
            self.sheet7_dict_ = {}
            
            self.gene_sheet_array_ = []
            
            self.src_dict_ = {
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
                    },
                    "手动输入数据": {
                        '实收资本':30000000,
                        '单元资产净值': None, 
                        '总份额': None,
                        "返息":None,
                        "手续费":None
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
                            "总市值": None,
                            "去锁市值":None
                        },
                        'isOpen':True                        
                    },
                    "手动输入数据": {
                        '实收资本':10000000,
                        '总份额': None,
                        '账户资产净值': None,
                        '占用': None,
                        "返息":None,
                        "手续费":None,
                        "当日盈亏":None,
                        "平仓盈亏":None
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
                    },
                    "手动输入数据": {
                        '实收资本':5000000,
                        '账户资产净值': None,
                        '总份额': None,
                        "返息":100,
                        "手续费":None
                    }                     
                }                
            }
            
            self.read_detail_config()    
                            
        except Exception as e:
            logging.error(f"读取基本信息出错: {e}")  

    def InitDataDict(self, data_read_obj):
        try:

            init_excel_file(self.file_path_,self.src_dict_, data_read_obj)

            if self.src_dict_ is None:
                logging.critical("初始化 Excel 文件失败。")

            self.read_jz_info()
        except Exception as e:
            logging.error(f"InitDataDict: {e}")  

    def read_industry(self):
        try:

            if '行业统计' in self.config_['量化二']:   
                src_industry_dict = self.config_['量化二']['行业统计']
                
                for item in self.industry_list_:
                    if item in src_industry_dict or item == '其他' or item =='合计':
                        self.industry_dict_[item] = {
                            '标的详情':[],
                            '统计数据': {
                                '标的列表':[],
                                '标的列表信息':'',
                                '多头市值': 0,
                                '空头市值': 0,
                                '净市值':0
                            }
                        }

                        if item in src_industry_dict:
                            self.industry_dict_[item]['标的详情'] = read_json_array(src_industry_dict[item], item)
                    else:
                        logging.error(f"量化二行业统计 缺少 ${item}") 

                # logging.info(self.industry_dict_)
                                                                             
            else:
                logging.critical("配置文件中未找到 '量化二-行业统计' 字段，请检查。")       
        except Exception as e:
            logging.error(f"读取量化二行业统计信息出错: {e}")  
            return None       
                    
    def read_detail_config(self):   
        try:
            if '量化一' in self.config_:
                if '投机单元-单元资产净值' in self.config_['量化一']:                   
                    self.src_dict_['量化一']['手动输入数据']['单元资产净值'] =  float(str(self.config_['量化一']['投机单元-单元资产净值']))
                    if self.src_dict_['量化一']['手动输入数据']['单元资产净值'] is None:
                        logging.critical("配置文件中 '量化一-投机单元-单元资产净值' 字段读取失败，请检查。")                    
                else:
                    logging.critical("配置文件中未找到 '量化一-投机单元-单元资产净值' 字段，请检查。")
                    
                if '总份额'  in self.config_['量化一']:                                     
                    self.src_dict_['量化一']['手动输入数据']['总份额'] = float(str(self.config_['量化一']['总份额'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化一']['手动输入数据']['总份额'] is None:
                        logging.critical("配置文件中 '量化一-总份额' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化一-总份额' 字段，请检查。")   
                    
                if '返息'  in self.config_['量化一']:                                     
                    self.src_dict_['量化一']['手动输入数据']['返息'] = float(str(self.config_['量化一']['返息'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化一']['手动输入数据']['返息'] is None:
                        logging.critical("配置文件中 '量化一-返息' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化一-返息' 字段，请检查。")               
                    
                if '手续费'  in self.config_['量化一']:                                     
                    self.src_dict_['量化一']['手动输入数据']['手续费'] = float(str(self.config_['量化一']['手续费'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化一']['手动输入数据']['手续费'] is None:
                        logging.critical("配置文件中 '量化一-手续费' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化一-手续费' 字段，请检查。")                              
                    
                if '实收资本'  in self.config_['量化一']:                                     
                    self.src_dict_['量化一']['手动输入数据']['实收资本'] = float(str(self.config_['量化一']['实收资本'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化一']['手动输入数据']['实收资本'] is None:
                        logging.critical("配置文件中 '量化一-实收资本' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化一-实收资本' 字段，请检查。")                       
                                              
                
            else:
                logging.critical("配置文件中未找到 '量化一' 字段，请检查。")
            
            if '量化二' in self.config_:
                if '账户资产净值' in self.config_['量化二']:                   
                    self.src_dict_['量化二']['手动输入数据']['账户资产净值'] =  float(str(self.config_['量化二']['账户资产净值']))
                    if self.src_dict_['量化二']['手动输入数据']['账户资产净值'] is None:
                        logging.critical("配置文件中 '量化二-账户资产净值' 字段读取失败，请检查。")                    
                else:
                    logging.critical("配置文件中未找到 '量化二-账户资产净值' 字段，请检查。")
                    
                if '总份额'  in self.config_['量化二']:                                     
                    self.src_dict_['量化二']['手动输入数据']['总份额'] = float(str(self.config_['量化二']['总份额'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化二']['手动输入数据']['总份额'] is None:
                        logging.critical("配置文件中 '量化二-总份额' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化二-总份额' 字段，请检查。")   
                                       
                    
                if '手续费'  in self.config_['量化二']:                                     
                    self.src_dict_['量化二']['手动输入数据']['手续费'] = float(str(self.config_['量化二']['手续费'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化二']['手动输入数据']['手续费'] is None:
                        logging.critical("配置文件中 '量化二-手续费' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化二-手续费' 字段，请检查。")     
                    
                if '返息'  in self.config_['量化二']:                                     
                    self.src_dict_['量化二']['手动输入数据']['返息'] = float(str(self.config_['量化二']['返息'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化二']['手动输入数据']['返息'] is None:
                        logging.critical("配置文件中 '量化二-返息' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化二-返息' 字段，请检查。")                        
                    
                if '实收资本'  in self.config_['量化二']:                                     
                    self.src_dict_['量化二']['手动输入数据']['实收资本'] = float(str(self.config_['量化二']['实收资本'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化二']['手动输入数据']['实收资本'] is None:
                        logging.critical("配置文件中 '量化二-实收资本' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化二-实收资本' 字段，请检查。")     

                if '当日盈亏'  in self.config_['量化二']:                                     
                    self.src_dict_['量化二']['手动输入数据']['当日盈亏'] = float(str(self.config_['量化二']['当日盈亏'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化二']['手动输入数据']['当日盈亏'] is None:
                        logging.critical("配置文件中 '量化二-当日盈亏' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化二-当日盈亏' 字段，请检查。")                        
                    
                if '平仓盈亏'  in self.config_['量化二']:                                     
                    self.src_dict_['量化二']['手动输入数据']['平仓盈亏'] = float(str(self.config_['量化二']['平仓盈亏'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化二']['手动输入数据']['平仓盈亏'] is None:
                        logging.critical("配置文件中 '量化二-平仓盈亏' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化二-平仓盈亏' 字段，请检查。")      

                self.read_industry()                                                        
                                                                                  
            else:
                logging.critical("配置文件中未找到 '量化二' 字段，请检查。")
            
            if '量化三' in self.config_:
                if '账户资产净值' in self.config_['量化三']:                   
                    self.src_dict_['量化三']['手动输入数据']['账户资产净值'] =  float(str(self.config_['量化三']['账户资产净值']))
                    if self.src_dict_['量化三']['手动输入数据']['账户资产净值'] is None:
                        logging.critical("配置文件中 '量化三-账户资产净值' 字段读取失败，请检查。")                    
                else:
                    logging.critical("配置文件中未找到 '量化三-账户资产净值' 字段，请检查。")
                                       
                if '总份额'  in self.config_['量化三']:                                     
                    self.src_dict_['量化三']['手动输入数据']['总份额'] = float(str(self.config_['量化三']['总份额'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化三']['手动输入数据']['总份额'] is None:
                        logging.critical("配置文件中 '量化三-总份额' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化三-总份额' 字段，请检查。")                                          
                    
                if '返息'  in self.config_['量化三']:                                     
                    self.src_dict_['量化三']['手动输入数据']['返息'] = float(str(self.config_['量化三']['返息'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化三']['手动输入数据']['返息'] is None:
                        logging.critical("配置文件中 '量化三-返息' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化三-返息' 字段，请检查。")   
                    
                if '手续费'  in self.config_['量化三']:                                     
                    self.src_dict_['量化三']['手动输入数据']['手续费'] = float(str(self.config_['量化三']['手续费'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化三']['手动输入数据']['手续费'] is None:
                        logging.critical("配置文件中 '量化三-手续费' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化三-手续费' 字段，请检查。")                         
                    
                if '实收资本'  in self.config_['量化三']:                                     
                    self.src_dict_['量化三']['手动输入数据']['实收资本'] = float(str(self.config_['量化三']['实收资本'])) #手动输入的单元资产净值;
                    if self.src_dict_['量化三']['手动输入数据']['实收资本'] is None:
                        logging.critical("配置文件中 '量化三-实收资本' 字段值为空，请检查。")
                else:
                    logging.critical("配置文件中未找到 '量化三-实收资本' 字段，请检查。")                                          
                                              
                                    
            else:
                logging.critical("配置文件中未找到 '量化三' 字段，请检查。")     
                
            # logging.info(f"读取配置文件成功。\n量化一手动输入信息: {self.src_dict_['量化一']['手动输入数据']}\n量化二手动输入信息: {self.src_dict_['量化二']['手动输入数据']}\n量化三手动输入信息: {self.src_dict_['量化三']['手动输入数据']}")       
                  
                
            if '是否绘制净值曲线' in self.config_:
                self.draw_net_value_curve_ = self.config_['是否绘制净值曲线']
            else:
                self.draw_net_value_curve_ = 0
                
            if '绘制折线图天数' in self.config_:
                self.draw_line_days_ = int(self.config_['绘制折线图天数'])
            else:
                self.draw_line_days_ = 15
                            
        except Exception as e:
            logging.error(f"读取配置文件出错: {e}")  
            return None
                                  
    def read_jz_info(self):
        try:
            self.jz_ = {
                '量化一':
                    {
                        '结算数据': JZData('量化一-结算数据'),
                        '收盘数据': JZData('量化一-收盘数据'),
                    },
                '量化二':
                    {
                        '结算数据': JZData('量化二-结算数据'),
                        '收盘数据': JZData('量化二-收盘数据'),
                    },
                '量化三':
                    {
                        '结算数据': JZData('量化三-结算数据'),
                        '收盘数据': JZData('量化三-收盘数据'),
                    },
            }
            if '量化一-结算数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化一-结算数据']                
                self.jz_['量化一']['结算数据'].read_data_from_excel_sheet(sheet, '量化一-结算数据')                
            else:   
                logging.critical("文件中未找到 量化一-结算数据 表格，请检查。")
                            
            if '量化一-收盘数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化一-收盘数据']
                self.jz_['量化一']['收盘数据'].read_data_from_excel_sheet(sheet, '量化一-收盘数据')
            else:
                logging.critical("文件中未找到 量化一-收盘数据 表格，请检查。")
                
                
                            
            if '量化二-结算数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化二-结算数据']
                self.jz_['量化二']['结算数据'].read_data_from_excel_sheet(sheet, '量化二-结算数据')
            else:
                logging.critical("文件中未找到 量化二-结算数据 表格，请检查。")
                
                
            if '量化二-收盘数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化二-收盘数据']
                self.jz_['量化二']['收盘数据'].read_data_from_excel_sheet(sheet, '量化二-收盘数据')                                
            else:
                logging.critical("文件中未找到 量化二-收盘数据 表格，请检查。")

            if '量化三-结算数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化三-结算数据']
                self.jz_['量化三']['结算数据'].read_data_from_excel_sheet(sheet, '量化三-结算数据')
            else:
                logging.critical("文件中未找到 量化三-结算数据 表格，请检查。")
                
                
            if '量化三-收盘数据' in self.jz_workbook_.sheetnames:
                sheet = self.jz_workbook_['量化三-收盘数据']
                self.jz_['量化三']['收盘数据'].read_data_from_excel_sheet(sheet, '量化三-收盘数据')                                                           
            else:
                logging.critical("文件中未找到 量化三-收盘数据 表格，请检查。")                
                        
        except Exception as e:
            logging.error(f"读取净值信息出错: {e}")  
                                                                                                                                               
    def set_new_jz_info(self):
        try:
            dt = datetime.strptime(self.date, '%Y-%m-%d')
            tmp_date = dt.strftime('%Y/%m/%d')
                                
            try:
                if self.src_dict_['量化一']['其余信息']['isOpen'] is True:
                    if '量化一-结算数据' in self.jz_workbook_.sheetnames and '量化一-结算数据' in self.gene_sheet_array_:
                        sheet = self.jz_workbook_['量化一-结算数据']
                        last_row = get_last_row(sheet, '量化一-结算数据')
                        sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                        sheet.cell(row = last_row+1, column = 2, value = round(self.jz_['量化一']['结算数据'].jz_list_with_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 4, value = round(self.jz_['量化一']['结算数据'].jz_list_no_profit_[-1], 5))
                        
                        # logging.info(f"hc_list_with_profit_.size: {len(self.jz_['量化一']['结算数据'].hc_list_with_profit_)}, hc_list_no_profit_.size: {self.jz_['量化一']['结算数据'].hc_list_no_profit_}")
                        
                        for i in range(0, last_row):
                            sheet.cell(row = i+2, column = 3, value = str(round(self.jz_['量化一']['结算数据'].hc_list_with_profit_[i]*100, 4)) + '%')
                            sheet.cell(row = i+2, column = 5, value = str(round(self.jz_['量化一']['结算数据'].hc_list_no_profit_[i]*100, 4)) + '%')
                    else:
                        logging.critical("文件中未找到 量化一-结算数据 表格，请检查。")
                        
                    if '量化一-收盘数据' in self.jz_workbook_.sheetnames and '量化一-收盘数据' in self.gene_sheet_array_:
                        sheet = self.jz_workbook_['量化一-收盘数据']
                        last_row = get_last_row(sheet, '量化一-收盘数据')                    
                        sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                        sheet.cell(row = last_row+1, column = 2, value = round(self.jz_['量化一']['收盘数据'].jz_list_with_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 4, value = round(self.jz_['量化一']['收盘数据'].jz_list_no_profit_[-1], 5))
                        
                        for i in range(0, last_row):       
                            sheet.cell(row = i+2, column = 3, value = str(round(self.jz_['量化一']['收盘数据'].hc_list_with_profit_[i]*100, 4)) + '%')
                            sheet.cell(row = i+2, column = 5, value = str(round(self.jz_['量化一']['收盘数据'].hc_list_no_profit_[i]*100, 4)) + '%')
                    else:
                        logging.critical("文件中未找到 量化一-收盘数据 表格，请检查。")
            except Exception as e:
                logging.error(f"设置量化一新净值信息出错: {e}")  
            
            try:
                if self.src_dict_['量化二']['其余信息']['isOpen'] is True:
                    if '量化二-结算数据' in self.jz_workbook_.sheetnames and '量化二-结算数据' in self.gene_sheet_array_:
                        sheet = self.jz_workbook_['量化二-结算数据']
                        last_row = get_last_row(sheet, '量化二-结算数据')
                        sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                        sheet.cell(row = last_row+1, column = 2, value = round(self.jz_['量化二']['结算数据'].jz_list_with_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 4, value = round(self.jz_['量化二']['结算数据'].jz_list_no_profit_[-1], 5))
                        
                        # logging.info(f"hc_list_with_profit_.size: {len(self.jz_['量化二']['结算数据'].hc_list_with_profit_)}, hc_list_no_profit_.size: {self.jz_['量化一']['结算数据'].hc_list_no_profit_}")
                        
                        for i in range(0, last_row):
                            sheet.cell(row = i+2, column = 3, value = str(round(self.jz_['量化二']['结算数据'].hc_list_with_profit_[i]*100, 4)) + '%')
                            sheet.cell(row = i+2, column = 5, value = str(round(self.jz_['量化二']['结算数据'].hc_list_no_profit_[i]*100, 4)) + '%')
                    else:
                        logging.critical("文件中未找到 量化二-结算数据 表格，请检查。")
                        
                    if '量化二-收盘数据' in self.jz_workbook_.sheetnames and '量化二-收盘数据' in self.gene_sheet_array_:
                        sheet = self.jz_workbook_['量化二-收盘数据']
                        last_row = get_last_row(sheet, '量化二-收盘数据')
                        sheet.cell(row = last_row+1, column = 2, value = round(self.jz_['量化二']['收盘数据'].jz_list_with_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 4, value = round(self.jz_['量化二']['收盘数据'].jz_list_no_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                        
                        for i in range(0, last_row):       
                            sheet.cell(row = i+2, column = 3, value = str(round(self.jz_['量化二']['收盘数据'].hc_list_with_profit_[i]*100, 4)) + '%')
                            sheet.cell(row = i+2, column = 5, value = str(round(self.jz_['量化二']['收盘数据'].hc_list_no_profit_[i]*100, 4)) + '%')
                    else:
                        logging.critical("文件中未找到 量化二-收盘数据 表格，请检查。")       
            except Exception as e:
                logging.error(f"设置 量化二 新净值信息出错: {e}")     
                
                                  
            try:
                if self.src_dict_['量化三']['其余信息']['isOpen'] is True:
                    if '量化三-结算数据' in self.jz_workbook_.sheetnames and '量化三-结算数据' in self.gene_sheet_array_:
                        sheet = self.jz_workbook_['量化三-结算数据']
                        last_row = get_last_row(sheet, '量化三-结算数据')
                        sheet.cell(row = last_row+1, column = 2, value = round(self.jz_['量化三']['结算数据'].jz_list_with_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 4, value = round(self.jz_['量化三']['结算数据'].jz_list_no_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                        
                        # logging.info(f"hc_list_with_profit_.size: {len(self.jz_['量化三']['结算数据'].hc_list_with_profit_)}, hc_list_no_profit_.size: {self.jz_['量化一']['结算数据'].hc_list_no_profit_}")
                        
                        for i in range(0, last_row):
                            sheet.cell(row = i+2, column = 3, value = str(round(self.jz_['量化三']['结算数据'].hc_list_with_profit_[i]*100, 4)) + '%')
                            sheet.cell(row = i+2, column = 5, value = str(round(self.jz_['量化三']['结算数据'].hc_list_no_profit_[i]*100, 4)) + '%')
                    else:
                        logging.critical("文件中未找到 量化三-结算数据 表格，请检查。")
                        
                    if '量化三-收盘数据' in self.jz_workbook_.sheetnames and '量化三-收盘数据' in self.gene_sheet_array_:
                        sheet = self.jz_workbook_['量化三-收盘数据']
                        last_row = get_last_row(sheet, '量化三-收盘数据')
                        sheet.cell(row = last_row+1, column = 2, value = round(self.jz_['量化三']['收盘数据'].jz_list_with_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 4, value = round(self.jz_['量化三']['收盘数据'].jz_list_no_profit_[-1], 5))
                        sheet.cell(row = last_row+1, column = 1, value = tmp_date).number_format = numbers.FORMAT_DATE_YYYYMMDD2
                        
                        for i in range(0, last_row):       
                            sheet.cell(row = i+2, column = 3, value = str(round(self.jz_['量化三']['收盘数据'].hc_list_with_profit_[i]*100, 4)) + '%')
                            sheet.cell(row = i+2, column = 5, value = str(round(self.jz_['量化三']['收盘数据'].hc_list_no_profit_[i]*100, 4)) + '%')
                    else:
                        logging.critical("文件中未找到 量化三-收盘数据 表格，请检查。")     
                    
            except Exception as e:
                logging.error(f"设置 量化三 新净值信息出错: {e}")                                                            
            
            self.jz_workbook_.save(self.file_path_ + '/净值.xlsx')
        except Exception as e:
            logging.error(f"设置新净值信息出错: {e}")  

                   
    def Work(self):
        
        # print(self.src_dict_)
        if self.src_dict_['量化一']['其余信息']['isOpen'] is True:
            self.gene_first_sheet()
            self.gene_second_sheet()
           
        if self.src_dict_['量化二']['其余信息']['isOpen'] is True:
            self.gene_third_sheet()
            self.gene_fourth_sheet()   
            

        if self.src_dict_['量化三']['其余信息']['isOpen'] is True:
            self.gene_fivth_sheet()
            self.gene_sixth_sheet()    

        if self.src_dict_['量化二']['其余信息']['isOpen'] is True:
            self.gene_seven_sheet()  

                        
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
    
    def set_sheet_font(self, sheet, sheet_dict, sheet_name):
        try:
            for key, excel_data in sheet_dict.items():
                if excel_data is not None:
                    if key != '统计日期' and key != '注释':

                        sheet.cell(row = excel_data.row_, column = 1, value = key).font = self.bold_font_
                        sheet.cell(row = excel_data.row_, column = 1, value = key).border = self.border_
                        sheet.cell(row = excel_data.row_, column = 2, value = key).border = self.border_
                        sheet.cell(row = excel_data.row_, column = 2, value = key).font = self.no_bold_font_
                    
                        if '量化一' in sheet_name:
                            sheet.cell(row = excel_data.row_, column = 3, value = key).font = self.no_bold_font_
                            sheet.cell(row = excel_data.row_, column = 3, value = key).border = self.border_
                    else:
                        sheet.cell(row = excel_data.row_, column = 1, value = key).font = self.no_bold_font_   
                        sheet.cell(row = excel_data.row_, column = 2, value = key).font = self.no_bold_font_ 
                        if '量化一' in sheet_name:
                            sheet.cell(row = excel_data.row_, column = 3, value = key).font = self.no_bold_font_                        
                        
        except Exception as e:
            logging.error(f"{sheet_name} 设置字体出错: {e}")
            
    def gene_first_sheet(self):
        try:
            try:
                item_array = ['统计日期', 
                            '一、账户资产及收益情况', '账户名称', '账户编号', '资产单元名称', '单元资产净值', '账户资产净值', '返息、逆回购','手续费',
                            '总盈利/亏损(含返息、逆回购、手续费)', '收益率(含返息、逆回购、手续费)', '总盈利/亏损(不含返息、逆回购、手续费)', '收益率(不含返息、逆回购、手续费)',
                            '二、净值列示', '实收资本', '资产净值', '总份额', '期初单位净值', 
                            '昨日单位净值(含返息、逆回购、手续费)', '单位净值(含返息、逆回购、手续费)', '日净值增长率(含返息、逆回购、手续费)','昨日单位净值(不含返息、逆回购、手续费)', '单位净值(不含返息、逆回购、手续费)', '日净值增长率(不含返息、逆回购、手续费)',
                            '三、保证金使用情况', '占用', '账户权益', '风险度',
                            '四、交易情况', '交易方向及数量',
                            '五、持仓情况', '持仓品种及数量',
                            '注释']
                

                tmp_index = 1
                for item in item_array:
                    self.sheet1_dict_[item] = ExcelData(row = tmp_index)
                    tmp_index += 1            
                
                sheet = self.target_workbook_.create_sheet(title='量化一-结算数据')
                
                merge_col_list = ['账户名称', '账户编号', '账户资产净值', '总盈利/亏损(不含返息、逆回购、手续费)', '收益率(不含返息、逆回购、手续费)','总盈利/亏损(含返息、逆回购、手续费)','收益率(含返息、逆回购、手续费)',
                                    '实收资本', '资产净值', '总份额', '期初单位净值', 
                                    '昨日单位净值(含返息、逆回购、手续费)', '单位净值(含返息、逆回购、手续费)', '日净值增长率(含返息、逆回购、手续费)',
                                    '昨日单位净值(不含返息、逆回购、手续费)', '单位净值(不含返息、逆回购、手续费)', '日净值增长率(不含返息、逆回购、手续费)']
                                                                                    
                self.set_sheet_font(sheet, self.sheet1_dict_, '量化一-结算数据')
                
                # 设置表头栏需要填充的底色
                sheet.cell(row = self.sheet1_dict_['统计日期'].row_, column = 3, value = "(金额单位：元)")        
                sheet.cell(row = self.sheet1_dict_['一、账户资产及收益情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet1_dict_['二、净值列示'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet1_dict_['三、保证金使用情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet1_dict_['四、交易情况'].row_, column = 1).fill = self.fill_        
                sheet.cell(row = self.sheet1_dict_['五、持仓情况'].row_, column = 1).fill = self.fill_
                
                # 设置与返息相关的栏目的填充色
                for key, value in self.sheet1_dict_.items():
                    if '含逆回购' in key and '不含逆回购' not in key:
                        sheet.cell(row = self.sheet1_dict_[key].row_, column = 1).fill = self.with_profit_color_
                    elif '不含逆回购' in key :
                        sheet.cell(row = self.sheet1_dict_[key].row_, column = 1).fill = self.no_profit_color_
            except Exception as e:
                logging.error(f"生成 量化一结算数据-基础信息设置 单元格时发生错误: {e}")                                              
                   
            ################# 一、账户资产及收益情况 相关设置;
            try:
                cell_count = 1             
                cell_col_index = {}
                self.sheet1_dict_['账户资产净值'].value_ = 0
                if self.src_dict_['量化一']['单元资产'] is not None:
                    cell_index = 1
                    for key, value in self.src_dict_['量化一']['单元资产'].items():
                        if key != '合计':
                            
                            dt = datetime.strptime(value['统计日期'], '%Y-%m-%d')
                            self.date = dt.strftime('%Y-%m-%d')
                                            
                            self.sheet1_dict_['统计日期'].value_ = self.date
                            set_value(sheet, 1,2,'统计日期', value, '量化一-单元资产',False)
                                                                    
                            self.sheet1_dict_['账户名称'].value_ = value['账户名称']                                       
                            set_value(sheet, self.sheet1_dict_['账户名称'].row_, 2,'账户名称', value, '量化一-单元资产',False, self.border_)
                            
                            self.sheet1_dict_['账户编号'].value_ = math.floor(float(value['账户编号']))                                            
                            sheet.cell(row = self.sheet1_dict_['账户编号'].row_, column = 2, value=self.sheet1_dict_['账户编号'].value_).border = self.border_
                            
                            self.sheet1_dict_['资产单元名称'].value_ = value['资产单元名称']
                            set_value(sheet, self.sheet1_dict_['资产单元名称'].row_, 1+cell_index,'资产单元名称', value, '量化一-单元资产',False, self.border_)
                            
                            self.sheet1_dict_['单元资产净值'].value_ = float(value['单元资产净值(净价)'])
                            set_value(sheet, self.sheet1_dict_['单元资产净值'].row_,1+cell_index,'单元资产净值(净价)', value, '量化一-单元资产', True,self.border_)
                            
                            cell_index += 1
                            cell_col_index[key] = cell_index                        
                                                
                            self.sheet1_dict_['账户资产净值'].value_ += float(value['单元资产净值(净价)'])                
                        else :
                            set_value(sheet, self.sheet1_dict_['账户资产净值'].row_,2,'单元资产净值(净价)', value, '量化一-单元资产',False, self.border_)

                            self.sheet1_dict_['账户资产净值'].value_ = float(value['单元资产净值(净价)'])
                    cell_count = cell_index
                    
                    sheet.cell(row = self.sheet1_dict_['账户资产净值'].row_, column = 2, value = self.sheet1_dict_['账户资产净值'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet1_dict_['账户资产净值'].row_, column = 2).border = self.border_

                else:
                    logging.warning("量化一-单元资产文件不存在。")
                
                jyshg_profit = 0 # 返息、逆回购
                if self.src_dict_['量化一']['交易所回购'] is not None:
                    if 'profit' in self.src_dict_['量化一']['交易所回购']:   
                        jyshg_profit = self.src_dict_['量化一']['交易所回购']['profit'] + self.src_dict_['量化一']['手动输入数据']['返息'] + self.src_dict_['量化一']['手动输入数据']['手续费']
                        
                        sheet.cell(row = self.sheet1_dict_['返息、逆回购'].row_, column = cell_col_index['权益类一单元'], value =self.src_dict_['量化一']['交易所回购']['profit']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet1_dict_['返息、逆回购'].row_, column = cell_col_index['权益类一单元']).border = self.border_
                        
                        sheet.cell(row = self.sheet1_dict_['返息、逆回购'].row_, column = cell_col_index['量化一-投机单元'], value =self.src_dict_['量化一']['手动输入数据']['返息']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet1_dict_['返息、逆回购'].row_, column = cell_col_index['量化一-投机单元']).border = self.border_
                        
                        sheet.cell(row = self.sheet1_dict_['手续费'].row_, column = cell_col_index['量化一-投机单元'], value =self.src_dict_['量化一']['手动输入数据']['手续费']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet1_dict_['手续费'].row_, column = cell_col_index['量化一-投机单元']).border = self.border_          
                        
                        sheet.cell(row = self.sheet1_dict_['手续费'].row_, column = cell_col_index['权益类一单元'], value="-" )
                        sheet.cell(row = self.sheet1_dict_['手续费'].row_, column = cell_col_index['权益类一单元']).border = self.border_                                      
                    else:
                        logging.warning("量化一-交易所回购文件不存在。")
                else:
                    logging.warning("量化一-交易所回购文件不存在。")
            
                self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_ = 0  #总盈利/亏损(不含返息、逆回购、手续费)
                if self.src_dict_['量化一']['汇总证券-合计'] is not None:
                    if 'profit' in self.src_dict_['量化一']['汇总证券-合计']:
                        
                        self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].value_ = self.sheet1_dict_['账户资产净值'].value_ - self.src_dict_['量化一']['手动输入数据']['实收资本'] #总盈利/亏损(含返息、逆回购、手续费)
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].value_,2))).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_ 
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_ 
                        
                        self.sheet1_dict_['收益率(含返息、逆回购、手续费)'].value_ = self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].value_ / self.src_dict_['量化一']['手动输入数据']['实收资本'] * 100 # 收益率(含返息、逆回购、手续费)
                        sheet.cell(row = self.sheet1_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet1_dict_['收益率(含返息、逆回购、手续费)'].value_, 4))+"%")
                        sheet.cell(row = self.sheet1_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet1_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_
                        sheet.cell(row = self.sheet1_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_

                        self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_ = self.sheet1_dict_['总盈利/亏损(含返息、逆回购、手续费)'].value_ - jyshg_profit                                   
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 2, value = self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                        sheet.cell(row = self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                        
                        self.sheet1_dict_['收益率(不含返息、逆回购、手续费)'].value_ = self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_ / self.src_dict_['量化一']['手动输入数据']['实收资本'] * 100
                        sheet.cell(row = self.sheet1_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet1_dict_['收益率(不含返息、逆回购、手续费)'].value_, 4))+"%")
                        sheet.cell(row = self.sheet1_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet1_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                        sheet.cell(row = self.sheet1_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_                        
                        
                    else:
                        logging.warning("量化一-汇总证券-合计文件不存在。")
                else:
                    logging.warning("量化一-汇总证券-合计文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化一结算数据-一、账户资产及收益情况 单元格时发生错误: {e}")                  
                
            
            ################# 二、净值列示设置                               
            try:
                self.sheet1_dict_['实收资本'].value_ = self.src_dict_['量化一']['手动输入数据']['实收资本']
                sheet.cell(row = self.sheet1_dict_['实收资本'].row_, column = 2, value = self.src_dict_['量化一']['手动输入数据']['实收资本']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet1_dict_['资产净值'].row_, column = 2, value = self.sheet1_dict_['账户资产净值'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet1_dict_['总份额'].row_, column = 2, value = self.src_dict_['量化一']['手动输入数据']['总份额']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet1_dict_['期初单位净值'].value_ = self.src_dict_['量化一']['手动输入数据']['实收资本']/self.src_dict_['量化一']['手动输入数据']['总份额'] #期初单位净值
                sheet.cell(row = self.sheet1_dict_['期初单位净值'].row_, column = 2, value = round(self.sheet1_dict_['期初单位净值'].value_, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                
                self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_ = self.jz_['量化一']['结算数据'].last_jz_with_profit_
                sheet.cell(row = self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].value_ = self.sheet1_dict_['账户资产净值'].value_ /self.src_dict_['量化一']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet1_dict_['日净值增长率(含返息、逆回购、手续费)'].value_ = (self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].value_ - self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_) / self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_ * 100
                # logging.info(f"单位净值(含返息、逆回购、手续费): {self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].value_}")
                # logging.info(f"昨日单位净值(含返息、逆回购、手续费): {self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_}")
                # logging.info(f"日净值增长率(含返息、逆回购、手续费): {self.sheet1_dict_['日净值增长率(含返息、逆回购、手续费)'].value_}")
                
                sheet.cell(row = self.sheet1_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet1_dict_['日净值增长率(含返息、逆回购、手续费)'].value_, 5)) + '%')  
                
                self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_ = self.jz_['量化一']['结算数据'].last_jz_no_profit_
                sheet.cell(row = self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].value_ = (self.sheet1_dict_['实收资本'].value_ + self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_) / self.src_dict_['量化一']['手动输入数据']['总份额'] #(实收资本 + 总盈利/亏损(不含返息、手续费)) / 总份额            
                sheet.cell(row = self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet1_dict_['日净值增长率(不含返息、逆回购、手续费)'].value_ = (self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].value_ - self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_)  / self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_ * 100                
                sheet.cell(row = self.sheet1_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet1_dict_['日净值增长率(不含返息、逆回购、手续费)'].value_, 5)) + '%')              
                
                sheet.cell(row = self.sheet1_dict_['实收资本'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet1_dict_['资产净值'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet1_dict_['总份额'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet1_dict_['期初单位净值'].row_, column = 2).border = self.border_
                
                sheet.cell(row = self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet1_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_

                sheet.cell(row = self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet1_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_                
                
                sheet.cell(row = self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet1_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_  
                
                sheet.cell(row = self.sheet1_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                sheet.cell(row = self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                sheet.cell(row = self.sheet1_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_                
                
                sheet.cell(row = self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                sheet.cell(row = self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                sheet.cell(row = self.sheet1_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_                          
                
                sheet.cell(row = self.sheet1_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet1_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_                      
                
                # 更新净值;
                self.jz_['量化一']['结算数据'].update_data(self.date, 
                                                        self.sheet1_dict_['单位净值(含返息、逆回购、手续费)'].value_, 
                                                        self.sheet1_dict_['单位净值(不含返息、逆回购、手续费)'].value_)                            
            except Exception as e:
                logging.error(f"生成 量化一结算数据-二、净值列示设置 单元格时发生错误: {e}")                              
            
            ################# 三、保证金使用情况设置;
            try:
                if self.src_dict_['量化一']['期货保证金分析'] is not None:
                    for key, value in self.src_dict_['量化一']['期货保证金分析'].items():
                        if key in cell_col_index:
                            set_value(sheet, self.sheet1_dict_['占用'].row_,cell_col_index[key],'占用保证金(静态)', value, '量化一-期货保证金分析',True, self.border_)
                            set_value(sheet, self.sheet1_dict_['账户权益'].row_,cell_col_index[key],'账户权益', value, '量化一-期货保证金分析', True, self.border_)                    
                            sheet.cell(row = self.sheet1_dict_['风险度'].row_, column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),3))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            sheet.cell(row = self.sheet1_dict_['风险度'].row_, column = cell_col_index[key]).border = self.border_
                        else:
                            logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                            
                    sheet.cell(row = self.sheet1_dict_['占用'].row_, column = 3, value="-").border = self.border_
                    sheet.cell(row = self.sheet1_dict_['账户权益'].row_, column = 3,value="-").border = self.border_
                    sheet.cell(row = self.sheet1_dict_['风险度'].row_, column = 3,value="-").border = self.border_
                else:
                    logging.warning("量化一-期货保证金分析文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化一结算数据-三、保证金使用情况设置 单元格时发生错误: {e}")                  
                
            ################# 四、交易情况;
            try:
                if self.src_dict_['量化一']['成交回报'] is not None:
                    set_value(sheet, self.sheet1_dict_['交易方向及数量'].row_,2,'future_info', self.src_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
                    set_value(sheet, self.sheet1_dict_['交易方向及数量'].row_,3,'stock_info', self.src_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
                else:
                    logging.warning("量化一-成交回报文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化一结算数据-四、交易情况 单元格时发生错误: {e}")                
                
            ################# 五、持仓情况;
            try:
                if self.src_dict_['量化一']['汇总证券-当日持仓'] is not None:
                    set_value(sheet, self.sheet1_dict_['持仓品种及数量'].row_,2,'future_info', self.src_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓',False, self.border_)
                    set_value(sheet, self.sheet1_dict_['持仓品种及数量'].row_,3,'stock_info', self.src_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
                else:
                    logging.warning("量化一-汇总证券-当日持仓文件不存在。")     

            except Exception as e:
                logging.error(f"生成 量化一结算数据-五、持仓情况 单元格时发生错误: {e}")
                            
            
            ################# 注释;
            try:                
                extra_info = f"注:\n1、总盈利/亏损(不含逆回购): 根据032盈亏数据计算,未扣除中金所申报费。\n"
                extra_info += f"2、总盈利/亏损(含逆回购)：已扣除中金所申报费；按照O32盈亏数据计算的未扣除申报费的金额为：{round(self.src_dict_['量化一']['交易所回购']['profit'] + self.sheet1_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_,4)} 元。\n"
                extra_info += f"3、返息: {self.src_dict_['量化一']['手动输入数据']['返息']}元。\n"
                sheet.cell(row = self.sheet1_dict_['注释'].row_, column = 1, value = extra_info)
            except Exception as e:
                logging.error(f"生成 量化一结算数据-注释 单元格时发生错误: {e}")

            ################# 样式设置;
            try:           
                set_sheet_middle(sheet)
                sheet.column_dimensions['A'].width = 54
                # 设置第二列(B列)的宽度为10个字符
                sheet.column_dimensions['B'].width = 58
                # 设置第三列(C列)的宽度为15个字符
                sheet.column_dimensions['C'].width = 58        

                for key, value in self.sheet1_dict_.items():
                    if key == '交易方向及数量' or key == '持仓品种及数量':
                        sheet.row_dimensions[value.row_].height = 140 
                    elif key == '注释':
                        sheet.row_dimensions[value.row_].height = 80
                    else:
                        sheet.row_dimensions[value.row_].height = 32
                
                sheet.cell(row = self.sheet1_dict_['交易方向及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
                sheet.cell(row = self.sheet1_dict_['交易方向及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
                sheet.cell(row = self.sheet1_dict_['持仓品种及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
                sheet.cell(row = self.sheet1_dict_['持仓品种及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                sheet.cell(row = self.sheet1_dict_['注释'].row_, column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                
                for key, value in self.sheet1_dict_.items():
                    if is_merge_all(key):
                        sheet.merge_cells(start_row=value.row_, start_column=1, end_row=value.row_, end_column=cell_count)
                    elif key in merge_col_list:
                        sheet.merge_cells(start_row=value.row_, start_column=2, end_row=value.row_, end_column=cell_count)
                    
            except Exception as e:
                logging.error(f"生成 量化一结算数据-最后样式设计 单元格时发生错误: {e}")                                        
                    
            self.jz_['量化一']['结算数据'].draw_chart(self.draw_line_days_, self.file_path_, 
                                                    self.draw_net_value_curve_, sheet, '量化一-结算数据')      
            
            self.gene_sheet_array_.append('量化一-结算数据')
        except Exception as e:
            logging.error(f"生成 量化一-结算数据 表格时发生错误: {e}")             
                
    def gene_second_sheet(self):
        try:
            try:
                sheet = self.target_workbook_.create_sheet(title='量化一-收盘数据')
                
                item_array = ['统计日期', 
                            '一、账户资产及收益情况', '账户名称', '账户编号', '资产单元名称', '单元资产净值', '账户资产净值', '返息、逆回购','手续费',
                            '盈利/亏损(含返息、逆回购、手续费)','总盈利/亏损(含返息、逆回购、手续费)', '收益率(含返息、逆回购、手续费)', '盈利/亏损(不含返息、逆回购、手续费)', '总盈利/亏损(不含返息、逆回购、手续费)', '收益率(不含返息、逆回购、手续费)',
                            '二、净值列示', '实收资本', '资产净值', '总份额', '期初单位净值', 
                            '昨日单位净值(含返息、逆回购、手续费)', '单位净值(含返息、逆回购、手续费)', '日净值增长率(含返息、逆回购、手续费)','昨日单位净值(不含返息、逆回购、手续费)', '单位净值(不含返息、逆回购、手续费)', '日净值增长率(不含返息、逆回购、手续费)',
                            '三、保证金使用情况', '占用', '账户权益', '风险度',
                            '四、交易情况', '交易方向及数量',
                            '五、持仓情况', '持仓品种及数量',
                            '注释']
                
                tmp_index = 1
                for item in item_array:
                    self.sheet2_dict_[item] = ExcelData(row = tmp_index)
                    tmp_index += 1            
                            
                merge_col_list = ['账户名称', '账户编号', '账户资产净值',  '总盈利/亏损(不含返息、逆回购、手续费)', '收益率(不含返息、逆回购、手续费)',
                                '总盈利/亏损(含返息、逆回购、手续费)','收益率(含返息、逆回购、手续费)',
                                '实收资本', '资产净值', '总份额', '期初单位净值', 
                                '昨日单位净值(含返息、逆回购、手续费)', '单位净值(含返息、逆回购、手续费)', '日净值增长率(含返息、逆回购、手续费)',
                                '昨日单位净值(不含返息、逆回购、手续费)', '单位净值(不含返息、逆回购、手续费)', '日净值增长率(不含返息、逆回购、手续费)']
                                            
                self.set_sheet_font(sheet, self.sheet2_dict_, '量化一-收盘数据')

                sheet.cell(row = 1, column = 3, value = "(金额单位：元)")
                
                sheet.cell(row = self.sheet2_dict_['统计日期'].row_, column = 3, value = "(金额单位：元)")        
                sheet.cell(row = self.sheet2_dict_['一、账户资产及收益情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet2_dict_['二、净值列示'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet2_dict_['三、保证金使用情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet2_dict_['四、交易情况'].row_, column = 1).fill = self.fill_        
                sheet.cell(row = self.sheet2_dict_['五、持仓情况'].row_, column = 1).fill = self.fill_
                        
                
            
                cell_count = 1             
                cell_col_index = {}
                self.sheet2_dict_['账户资产净值'].value_ = 0 #账户资产净值;
                self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].value_ = 0 #汇总证券-合计-股票 总体盈亏
                if self.src_dict_['量化一']['汇总证券-合计-股票'] is not None:
                    if 'ztyk' in self.src_dict_['量化一']['汇总证券-合计-股票']:
                        self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].value_ = round(float(self.src_dict_['量化一']['汇总证券-合计-股票']['ztyk']),2)
                    else:
                        logging.warning("量化一-汇总证券-合计-股票文件不存在。")
                else:
                    logging.warning("量化一-汇总证券-合计-股票文件不存在。")
                    
                    
            except Exception as e:
                logging.error(f"生成 量化一收盘数据-基础信息设置 单元格时发生错误: {e}")              
                
            this_date = None
            ################# 一、账户资产及收益情况 相关设置;
            try:
                if self.src_dict_['量化一']['单元资产'] is not None:
                    cell_index = 1
                    for key, value in self.src_dict_['量化一']['单元资产'].items():
                        if key != '合计':
                            
                            dt = datetime.strptime(value['统计日期'], '%Y-%m-%d')
                            this_date = dt.strftime('%Y-%m-%d')
                            self.date = this_date
                                                        
                            set_value(sheet, self.sheet2_dict_['统计日期'].row_, 2, '统计日期', value, '量化一-单元资产', False)
                            set_value(sheet, self.sheet2_dict_['账户名称'].row_,2,'账户名称', value, '量化一-单元资产', False,self.border_)
                            self.sheet2_dict_['账户编号'].value_ =  re.sub(r'\.0$', '', value['账户编号'])
                            sheet.cell(row = self.sheet2_dict_['账户编号'].row_, column = 2, value=self.sheet2_dict_['账户编号'].value_).border = self.border_
                            
                            if '量化一-投机单元' in key:
                                sheet.cell(row = self.sheet2_dict_['单元资产净值'].row_, column = 1+cell_index, value=self.src_dict_['量化一']['手动输入数据']['单元资产净值']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 单元资产净值 = 手动输入
                                sheet.cell(row = self.sheet2_dict_['单元资产净值'].row_, column = 1+cell_index).border = self.border_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index, value=self.src_dict_['量化一']['手动输入数据']['单元资产净值']-6000000).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损(不含返息、逆回购、手续费) = 单元资产净值-600万元
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index).border = self.border_
                                
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index).fill = self.no_profit_color_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                            set_value(sheet, self.sheet2_dict_['资产单元名称'].row_, 1+cell_index, '资产单元名称', value, '量化一-单元资产', False, self.border_)
                            
                            
                            if '量化一-投机单元' in key:
                                sheet.cell(row = self.sheet2_dict_['单元资产净值'].row_, column = 1+cell_index, value=self.src_dict_['量化一']['手动输入数据']['单元资产净值']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 单元资产净值 = 手动输入
                                sheet.cell(row = self.sheet2_dict_['单元资产净值'].row_, column = 1+cell_index).border = self.border_
                                
                                profit_fx = self.src_dict_['量化一']['手动输入数据']['单元资产净值']-6000000 - self.src_dict_['量化一']['手动输入数据']['返息']                            
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index, value=profit_fx).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损(不含返息、逆回购、手续费) = 单元资产净值-600万元
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index).border = self.border_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index).fill = self.no_profit_color_
                                
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1+cell_index, value=round(self.src_dict_['量化一']['手动输入数据']['单元资产净值']-6000000,2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损(含返息、逆回购、手续费) = 盈利/亏损(不含逆回购
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1+cell_index).border = self.border_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1+cell_index).fill = self.with_profit_color_
                                                                
                                self.sheet2_dict_['账户资产净值'].value_ += self.src_dict_['量化一']['手动输入数据']['单元资产净值']
                            else:
                                set_value(sheet, 6,1+cell_index,'单元资产净值(净价)', value, '量化一-单元资产', True, self.border_) # 单元资产净值 = 《单元资产》“单元资产净值(净价)”权益类一单元
                                tmp_dyzcjz = float(value['单元资产净值(净价)'])                        
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1+cell_index, value=round(tmp_dyzcjz-2400*10000,2)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 #盈利/亏损(含返息、逆回购、手续费)= 单元资产净值-2400万
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1+cell_index).border = self.border_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1+cell_index).fill = self.with_profit_color_
                                
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index, value=self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 盈利/亏损(不含返息、逆回购、手续费) =《汇总证券(合计-股票)》“总体盈亏(含费用)”最后一行数值
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index).border = self.border_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1+cell_index).fill = self.no_profit_color_
                                sheet.cell(row = self.sheet2_dict_['盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                                self.sheet2_dict_['账户资产净值'].value_ += tmp_dyzcjz
                                
                            cell_index += 1
                            cell_col_index[key] = cell_index   

                    jyshg_profit = 0 # 返息、逆回购
                    if self.src_dict_['量化一']['交易所回购'] is not None:
                        if 'profit' in self.src_dict_['量化一']['交易所回购']:   
                            self.sheet2_dict_['返息、逆回购'].value_ = self.src_dict_['量化一']['交易所回购']['profit'] + self.src_dict_['量化一']['手动输入数据']['返息'] + self.src_dict_['量化一']['手动输入数据']['手续费']
                            sheet.cell(row = self.sheet2_dict_['返息、逆回购'].row_, column = cell_col_index['权益类一单元'], value = self.src_dict_['量化一']['交易所回购']['profit']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            sheet.cell(row = self.sheet2_dict_['返息、逆回购'].row_, column = cell_col_index['权益类一单元']).border = self.border_
                            
                            sheet.cell(row = self.sheet2_dict_['返息、逆回购'].row_, column = cell_col_index['量化一-投机单元'], value =self.src_dict_['量化一']['手动输入数据']['返息']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1                    
                            sheet.cell(row = self.sheet2_dict_['返息、逆回购'].row_, column = cell_col_index['量化一-投机单元']).border = self.border_
                            
                            sheet.cell(row = self.sheet2_dict_['手续费'].row_, column = cell_col_index['量化一-投机单元'], value =self.src_dict_['量化一']['手动输入数据']['手续费']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            sheet.cell(row = self.sheet2_dict_['手续费'].row_, column = cell_col_index['量化一-投机单元']).border = self.border_    
                            
                            sheet.cell(row = self.sheet2_dict_['手续费'].row_, column = cell_col_index['权益类一单元'], value="-" )
                            sheet.cell(row = self.sheet2_dict_['手续费'].row_, column = cell_col_index['权益类一单元']).border = self.border_                                                          
                        else:
                            logging.warning("量化一-交易所回购文件不存在。")
                    else:
                        logging.warning("量化一-交易所回购文件不存在。")                               
                                    
                    sheet.cell(row = self.sheet2_dict_['账户资产净值'].row_, column = 2, value=self.sheet2_dict_['账户资产净值'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet2_dict_['账户资产净值'].row_, column = 2).border = self.border_
                    
                    self.sheet2_dict_['总盈利/亏损(含返息、逆回购、手续费)'].value_ = self.sheet2_dict_['账户资产净值'].value_-self.src_dict_['量化一']['手动输入数据']['实收资本']
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 2, value=self.sheet2_dict_['总盈利/亏损(含返息、逆回购、手续费)'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_

                    self.sheet2_dict_['收益率(含返息、逆回购、手续费)'].value_ = (self.sheet2_dict_['账户资产净值'].value_ - self.src_dict_['量化一']['手动输入数据']['实收资本']) / self.src_dict_['量化一']['手动输入数据']['实收资本'] * 100 # 收益率(含返息、逆回购、手续费)= 总盈利/亏损(含逆回购)÷3000万元×100%【保留4位小数】
                    sheet.cell(row = self.sheet2_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet2_dict_['收益率(含返息、逆回购、手续费)'].value_,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet2_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                    sheet.cell(row = self.sheet2_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                    sheet.cell(row = self.sheet2_dict_['收益率(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_                    
                    
                    self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_ = self.sheet2_dict_['总盈利/亏损(含返息、逆回购、手续费)'].value_ - self.sheet2_dict_['返息、逆回购'].value_
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 2, value=self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                    sheet.cell(row = self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                    
                    self.sheet2_dict_['收益率(不含返息、逆回购、手续费)'].value_ = self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_/self.src_dict_['量化一']['手动输入数据']['实收资本'] * 100
                    sheet.cell(row = self.sheet2_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 2, value=str(round(self.sheet2_dict_['收益率(不含返息、逆回购、手续费)'].value_, 4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                    sheet.cell(row = self.sheet2_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                    sheet.cell(row = self.sheet2_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                    sheet.cell(row = self.sheet2_dict_['收益率(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                    

                    
                    cell_count = cell_index                
                else:
                    logging.warning("量化一-单元资产文件不存在。")
                                                           
            except Exception as e:
                logging.error(f"生成 量化一收盘数据-一、账户资产及收益情况 单元格时发生错误: {e}") 
                
            ################# 二、净值列示设置   
            try:                                                
                self.sheet2_dict_['实收资本'].value_ = self.src_dict_['量化一']['手动输入数据']['实收资本']
                sheet.cell(row = self.sheet2_dict_['实收资本'].row_, column = 2, value = self.sheet2_dict_['实收资本'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet2_dict_['资产净值'].row_, column = 2, value = self.sheet2_dict_['账户资产净值'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet2_dict_['总份额'].row_, column = 2, value = self.src_dict_['量化一']['手动输入数据']['总份额']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet2_dict_['期初单位净值'].value_ = self.src_dict_['量化一']['手动输入数据']['实收资本']/self.src_dict_['量化一']['手动输入数据']['总份额'] #期初单位净值
                sheet.cell(row = self.sheet2_dict_['期初单位净值'].row_, column = 2, value = round(self.sheet2_dict_['期初单位净值'].value_, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_ = self.jz_['量化一']['收盘数据'].last_jz_with_profit_ 
                sheet.cell(row = self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].value_ = self.sheet2_dict_['账户资产净值'].value_ / self.src_dict_['量化一']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet2_dict_['日净值增长率(含返息、逆回购、手续费)'].value_ = (self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].value_ - self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_) / self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].value_ * 100
                sheet.cell(row = self.sheet2_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet2_dict_['日净值增长率(含返息、逆回购、手续费)'].value_, 5)) + '%')          
                

                self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_ = self.jz_['量化一']['结算数据'].last_jz_no_profit_
                sheet.cell(row = self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].value_ = (self.sheet2_dict_['实收资本'].value_ + self.sheet2_dict_['总盈利/亏损(不含返息、逆回购、手续费)'].value_) / self.src_dict_['量化一']['手动输入数据']['总份额'] #(实收资本 + 总盈利/亏损(不含返息、手续费)) / 总份额            
                sheet.cell(row = self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 2, value = round(self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].value_, 5))
                
                self.sheet2_dict_['日净值增长率(不含返息、逆回购、手续费)'].value_ = (self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].value_ - self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_)  / self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].value_ * 100                
                sheet.cell(row = self.sheet2_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 2, value = str(round(self.sheet2_dict_['日净值增长率(不含返息、逆回购、手续费)'].value_, 5)) + '%')              
                
                
                sheet.cell(row = self.sheet2_dict_['实收资本'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet2_dict_['资产净值'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet2_dict_['总份额'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet2_dict_['期初单位净值'].row_, column = 2).border = self.border_
                
                sheet.cell(row = self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet2_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 2).border = self.border_

                sheet.cell(row = self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet2_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 2).fill = self.with_profit_color_  
                sheet.cell(row = self.sheet2_dict_['昨日单位净值(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                sheet.cell(row = self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_
                sheet.cell(row = self.sheet2_dict_['日净值增长率(含返息、逆回购、手续费)'].row_, column = 1).fill = self.with_profit_color_                                
                
                sheet.cell(row = self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet2_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 2).fill = self.no_profit_color_          
                sheet.cell(row = self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                sheet.cell(row = self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_
                sheet.cell(row = self.sheet2_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 1).fill = self.no_profit_color_          
                                
                
                sheet.cell(row = self.sheet2_dict_['昨日单位净值(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet2_dict_['日净值增长率(不含返息、逆回购、手续费)'].row_, column = 2).border = self.border_       
                
                # 更新净值;
                self.jz_['量化一']['收盘数据'].update_data(this_date, 
                                                        self.sheet2_dict_['单位净值(含返息、逆回购、手续费)'].value_, 
                                                        self.sheet2_dict_['单位净值(不含返息、逆回购、手续费)'].value_)                 
            
            except Exception as e:
                logging.error(f"生成 量化一收盘数据-二、净值列示设置 单元格时发生错误: {e}")  
                
                
            ################# 三、保证金使用情况设置;
            try:
                if self.src_dict_['量化一']['期货保证金分析'] is not None:
                    for key, value in self.src_dict_['量化一']['期货保证金分析'].items():
                        if key in cell_col_index:
                            set_value(sheet, self.sheet2_dict_['占用'].row_, cell_col_index[key],'占用保证金(静态)', value, '量化一-期货保证金分析', True)
                            sheet.cell(row = self.sheet2_dict_['账户权益'].row_, column = cell_col_index[key], value=self.src_dict_['量化一']['手动输入数据']['单元资产净值']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 单元资产净值
                            sheet.cell(row = self.sheet2_dict_['账户权益'].row_, column = cell_col_index[key]).border = self.border_
                            
                            self.sheet2_dict_['风险度'].value_ = float(value['占用保证金(静态)']) / self.src_dict_['量化一']['手动输入数据']['单元资产净值'] * 100 # 风险度 = 占用÷账户权益×100%【保留4位小数】                            
                            sheet.cell(row = self.sheet2_dict_['风险度'].row_, column = cell_col_index[key], value=str(round(self.sheet2_dict_['风险度'].value_,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 风险度 = 占用÷账户权益×100%【保留4位小数】
                            sheet.cell(row = self.sheet2_dict_['风险度'].row_, column = cell_col_index[key]).border = self.border_
                        else:
                            logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                    
                    sheet.cell(row = self.sheet2_dict_['占用'].row_, column = 3, value="-").border = self.border_
                    sheet.cell(row = self.sheet2_dict_['账户权益'].row_, column = 3,value="-").border = self.border_
                    sheet.cell(row = self.sheet2_dict_['风险度'].row_, column = 3,value="-").border = self.border_
                else:
                    logging.warning("量化一-期货保证金分析文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化一收盘数据-三、保证金使用情况设置 单元格时发生错误: {e}")                     
                                
            
            ################# 四、交易情况;
            try:
                if self.src_dict_['量化一']['成交回报'] is not None:
                    set_value(sheet, self.sheet2_dict_['交易方向及数量'].row_,2,'future_info', self.src_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
                    set_value(sheet, self.sheet2_dict_['交易方向及数量'].row_,3,'stock_info', self.src_dict_['量化一']['成交回报'], '量化一-成交回报',False, self.border_)
                else:
                    logging.warning("量化一-成交回报文件不存在。")

            except Exception as e:
                logging.error(f"生成 量化一收盘数据-四、交易情况 单元格时发生错误: {e}")                  
                        
            ################# 五、持仓情况;       
            try:
                if self.src_dict_['量化一']['汇总证券-当日持仓'] is not None:
                    set_value(sheet, self.sheet2_dict_['持仓品种及数量'].row_,2,'future_info', self.src_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
                    set_value(sheet, self.sheet2_dict_['持仓品种及数量'].row_,3,'stock_info', self.src_dict_['量化一']['汇总证券-当日持仓'], '量化一-汇总证券-当日持仓', False, self.border_)
                else:
                    logging.warning("量化一-汇总证券-当日持仓文件不存在。")  
            except Exception as e:
                logging.error(f"生成 量化一收盘数据-五、持仓情况 单元格时发生错误: {e}")                
                
            ################# 注释;
            try:
                extra_info = f"注:\n1、盈利/亏损(不含逆回购)数据暂未包含中金所申报费，盈利/亏损(含逆回购)数据已包含中金所申报费。"
                extra_info += f"\n2、返息: {self.src_dict_['量化一']['手动输入数据']['返息']}元。"
                sheet.cell(row = self.sheet2_dict_['注释'].row_, column = 1, value = extra_info)     
            except Exception as e:
                logging.error(f"生成 量化一收盘数据-注释 单元格时发生错误: {e}")                                            
            
            '''
            设置样式
            '''
            try:
                set_sheet_middle(sheet)

                sheet.column_dimensions['A'].width = 54
                # 设置第二列(B列)的宽度为10个字符
                sheet.column_dimensions['B'].width = 58
                # 设置第三列(C列)的宽度为15个字符
                sheet.column_dimensions['C'].width = 58        

                for key, value in self.sheet2_dict_.items():
                    if key == '交易方向及数量' or key == '持仓品种及数量':
                        sheet.row_dimensions[value.row_].height = 140 
                    elif key == '注释':
                        sheet.row_dimensions[value.row_].height = 80
                    else:
                        sheet.row_dimensions[value.row_].height = 32
                
                sheet.cell(row = self.sheet2_dict_['交易方向及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
                sheet.cell(row = self.sheet2_dict_['交易方向及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
                sheet.cell(row = self.sheet2_dict_['持仓品种及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
                sheet.cell(row = self.sheet2_dict_['持仓品种及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                sheet.cell(row = self.sheet2_dict_['注释'].row_, column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                
                for key, value in self.sheet2_dict_.items():
                    if is_merge_all(key):
                        sheet.merge_cells(start_row=value.row_, start_column=1, end_row=value.row_, end_column=cell_count)
                    elif key in merge_col_list:
                        sheet.merge_cells(start_row=value.row_, start_column=2, end_row=value.row_, end_column=cell_count)    
                        
                self.jz_['量化一']['收盘数据'].draw_chart(self.draw_line_days_, self.file_path_, self.draw_net_value_curve_, sheet, '量化一-收盘数据')             
                
            except Exception as e:
                logging.error(f"生成 量化一-收盘数据-最后样式设计 单元格时发生错误: {e}")                                                 
                    
            self.gene_sheet_array_.append('量化一-收盘数据')
        
        except Exception as e:
            logging.error(f"生成 量化一-收盘数据 表格时发生错误: {e}")
               
    def gene_third_sheet(self):
        try:
            
            try:
                item_arrary = ['统计日期', '一、账户资产及收益情况', '账户名称', '账户编号', '资产单元名称', '账户资产净值', 
                            '返息','手续费', '总盈利/亏损(含返息、手续费)', '收益率(含返息、手续费)', '总盈利/亏损(不含返息、手续费)', '收益率(不含返息、手续费)', 
                            '二、净值列示', '实收资本', '资产净值', '总份额', '期初单位净值', 
                            '昨日单位净值(含返息、手续费)', '单位净值(含返息、手续费)', '日净值增长率(含返息、手续费)', '昨日单位净值(不含返息、手续费)', '单位净值(不含返息、手续费)', '日净值增长率(不含返息、手续费)', 
                            '三、保证金使用情况', '占用', '账户权益', '风险度', '四、交易情况', '交易方向及数量', '五、持仓情况','持仓品种及数量']            
                
                tmp_index = 1
                for item in item_arrary:
                    self.sheet3_dict_[item] = ExcelData(row = tmp_index)
                    tmp_index += 1
                    
                sheet = self.target_workbook_.create_sheet(title='量化二-结算数据')
                                            
                self.set_sheet_font(sheet, self.sheet3_dict_, '量化二-结算数据')
                                        
                sheet.cell(row = self.sheet3_dict_['一、账户资产及收益情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet3_dict_['二、净值列示'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet3_dict_['三、保证金使用情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet3_dict_['四、交易情况'].row_, column = 1).fill = self.fill_        
                sheet.cell(row = self.sheet3_dict_['五、持仓情况'].row_, column = 1).fill = self.fill_
            
            except Exception as e:
                logging.error(f"生成 量化二-结算数据-基础信息设置 单元格时发生错误: {e}")              
                            
            this_date = None
            ################# 一、账户资产及收益情况 相关设置;
            try:
                cell_count = 1             
                cell_col_index = {}
                if self.src_dict_['量化二']['单元资产'] is not None:
                    cell_index = 1
                    for key, value in self.src_dict_['量化二']['单元资产'].items():
                        if key != '合计':
                            
                            dt = datetime.strptime(value['统计日期'], '%Y-%m-%d')
                            this_date = dt.strftime('%Y-%m-%d')
                            self.date = this_date
                                                        
                            sheet.cell(row = self.sheet3_dict_['统计日期'].row_, column = 2, value=str(value['统计日期']) + ", (金额单位：元)").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            # sheet.cell(row = self.sheet3_dict_['统计日期'], column = 2).border = self.border_
                            set_value(sheet, self.sheet3_dict_['账户名称'].row_,2,'账户名称', value, '量化二-单元资产', False,self.border_)
                            tmpzhbh = value['账户编号']
                            sheet.cell(row = self.sheet3_dict_['账户编号'].row_, column = 2, value=math.floor(float(tmpzhbh)))
                            sheet.cell(row = self.sheet3_dict_['账户编号'].row_, column = 2).border = self.border_
                            set_value(sheet, self.sheet3_dict_['资产单元名称'].row_,1+cell_index,'资产单元名称', value, '量化二-单元资产', False, self.border_)
                            
                            self.sheet3_dict_['账户资产净值'].value_ = float(value['单元资产净值(净价)'])
                            set_value(sheet, self.sheet3_dict_['账户资产净值'].row_,1+cell_index,'单元资产净值(净价)', value, '量化二-单元资产', True, self.border_)
                            
                            sheet.cell(row = self.sheet3_dict_['返息'].row_, column = 2, value=self.src_dict_['量化二']['手动输入数据']['返息'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet3_dict_['返息'].row_, column = 2).border = self.border_          
                            
                            sheet.cell(row = self.sheet3_dict_['手续费'].row_, column = 2, value=self.src_dict_['量化二']['手动输入数据']['手续费'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet3_dict_['手续费'].row_, column = 2).border = self.border_           
                                                                                                                                                              
                            cell_index += 1
                            cell_col_index[key] = cell_index    
                    # print(cell_col_index)
                    cell_count = cell_index
            
                else:
                    logging.warning("量化二-单元资产文件不存在。")
                    
                profits1 = 0  #总盈利/亏损(不含返息、逆回购、手续费)
                if self.src_dict_['量化二']['汇总证券-合计'] is not None:
                    if 'profit' in self.src_dict_['量化二']['汇总证券-合计']:
                        profits1 = self.src_dict_['量化二']['汇总证券-合计']['profit']
                        
                        self.sheet3_dict_['总盈利/亏损(含返息、手续费)'].value_ = self.sheet3_dict_['账户资产净值'].value_  - self.src_dict_['量化二']['手动输入数据']['实收资本']
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2, value = round(self.sheet3_dict_['总盈利/亏损(含返息、手续费)'].value_,4)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                        
                        self.sheet3_dict_['收益率(含返息、手续费)'].value_ = (self.sheet3_dict_['总盈利/亏损(含返息、手续费)'].value_) / self.src_dict_['量化二']['手动输入数据']['实收资本'] * 100 #收益率
                        sheet.cell(row = self.sheet3_dict_['收益率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet3_dict_['收益率(含返息、手续费)'].value_,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet3_dict_['收益率(含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet3_dict_['收益率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_ 
                        sheet.cell(row = self.sheet3_dict_['收益率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                        

                        self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].value_ = self.sheet3_dict_['账户资产净值'].value_  - self.src_dict_['量化二']['手动输入数据']['实收资本'] - self.src_dict_['量化二']['手动输入数据']['返息'] - self.src_dict_['量化二']['手动输入数据']['手续费']
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2, value = round(self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].value_,4)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                        sheet.cell(row = self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                        
                        self.sheet3_dict_['收益率(不含返息、手续费)'].value_ = (self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].value_) / self.src_dict_['量化二']['手动输入数据']['实收资本'] * 100 #收益率
                        sheet.cell(row = self.sheet3_dict_['收益率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet3_dict_['收益率(不含返息、手续费)'].value_,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet3_dict_['收益率(不含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet3_dict_['收益率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_ 
                        sheet.cell(row = self.sheet3_dict_['收益率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_                        
                        
                    else:
                        logging.warning("量化二-汇总证券-合计文件不存在。")
                else:
                    logging.warning("量化二-汇总证券-合计文件不存在。")
                    
            except Exception as e:
                logging.error(f"生成 量化二结算数据-一、账户资产及收益情况 单元格时发生错误: {e}")                  
                                

            ################# 二、净值列示设置   
            try:
                self.sheet3_dict_['实收资本'].value_ = self.src_dict_['量化二']['手动输入数据']['实收资本']                                                         
                sheet.cell(row = self.sheet3_dict_['实收资本'].row_, column = 2, value = self.sheet3_dict_['实收资本'].value_ ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet3_dict_['资产净值'].value_ = self.sheet3_dict_['账户资产净值'].value_  #资产净值
                sheet.cell(row = self.sheet3_dict_['资产净值'].row_, column = 2, value = self.sheet3_dict_['资产净值'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                sheet.cell(row = self.sheet3_dict_['总份额'].row_, column = 2, value = self.src_dict_['量化二']['手动输入数据']['总份额']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet3_dict_['期初单位净值'].value_ = self.sheet3_dict_['实收资本'].value_ / self.src_dict_['量化二']['手动输入数据']['总份额'] #期初单位净值
                sheet.cell(row = self.sheet3_dict_['期初单位净值'].row_, column = 2, value = round(self.sheet3_dict_['期初单位净值'].value_, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet3_dict_['昨日单位净值(含返息、手续费)'].value_ = self.jz_['量化二']['结算数据'].last_jz_with_profit_
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet3_dict_['昨日单位净值(含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                
                self.sheet3_dict_['单位净值(含返息、手续费)'].value_ = self.sheet3_dict_['账户资产净值'].value_ / self.src_dict_['量化二']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet3_dict_['单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet3_dict_['单位净值(含返息、手续费)'].value_ , 5))
                sheet.cell(row = self.sheet3_dict_['单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet3_dict_['单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet3_dict_['单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                
                
                self.sheet3_dict_['日净值增长率(含返息、手续费)'].value_ = (self.sheet3_dict_['单位净值(含返息、手续费)'].value_  - self.sheet3_dict_['昨日单位净值(含返息、手续费)'].value_) / self.sheet3_dict_['昨日单位净值(含返息、手续费)'].value_ * 100 #日净值增长率
                sheet.cell(row = self.sheet3_dict_['日净值增长率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet3_dict_['日净值增长率(含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet3_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).border = self.border_ 
                sheet.cell(row = self.sheet3_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_ 
                sheet.cell(row = self.sheet3_dict_['日净值增长率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_ 
                
                self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].value_ = self.jz_['量化二']['结算数据'].last_jz_no_profit_
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                self.sheet3_dict_['单位净值(不含返息、手续费)'].value_ = (self.sheet3_dict_['实收资本'].value_ +  self.sheet3_dict_['总盈利/亏损(不含返息、手续费)'].value_) / self.src_dict_['量化二']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet3_dict_['单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet3_dict_['单位净值(不含返息、手续费)'].value_ , 5))
                sheet.cell(row = self.sheet3_dict_['单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet3_dict_['单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet3_dict_['单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                
                self.sheet3_dict_['日净值增长率(不含返息、手续费)'].value_ = (self.sheet3_dict_['单位净值(不含返息、手续费)'].value_  - self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].value_) / self.sheet3_dict_['昨日单位净值(不含返息、手续费)'].value_ * 100 #日净值增长率
                sheet.cell(row = self.sheet3_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet3_dict_['日净值增长率(不含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet3_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).border = self.border_ 
                sheet.cell(row = self.sheet3_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_ 
                sheet.cell(row = self.sheet3_dict_['日净值增长率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_                 
                             
            
                sheet.cell(row = self.sheet3_dict_['实收资本'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet3_dict_['资产净值'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet3_dict_['总份额'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet3_dict_['期初单位净值'].row_, column = 2).border = self.border_
                
                self.jz_['量化二']['结算数据'].update_data(this_date, 
                                                        self.sheet3_dict_['单位净值(含返息、手续费)'].value_, 
                                                        self.sheet3_dict_['单位净值(不含返息、手续费)'].value_)                 
                                                                                                                 
            except Exception as e:
                logging.error(f"生成 量化二结算数据-二、净值列示设置 单元格时发生错误: {e}")                          
                                    
            ################# 三、保证金使用情况设置;
            try:                            
                if self.src_dict_['量化二']['期货保证金分析'] is not None:
                    for key, value in self.src_dict_['量化二']['期货保证金分析'].items():
                        if key in cell_col_index:
                            set_value(sheet, self.sheet3_dict_['占用'].row_,cell_col_index[key],'占用保证金(静态)', value, '量化二-期货保证金分析', True, self.border_)
                            set_value(sheet, self.sheet3_dict_['账户权益'].row_,cell_col_index[key],'账户权益', value, '量化二-期货保证金分析', True, self.border_)
                            self.sheet3_dict_['风险度'].value_ = float(value['风险比例1(%)'])
                            sheet.cell(row = self.sheet3_dict_['风险度'].row_, column = cell_col_index[key], value = str(round(self.sheet3_dict_['风险度'].value_,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            sheet.cell(row = self.sheet3_dict_['风险度'].row_, column = cell_col_index[key]).border = self.border_
                        else:
                            logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                else:
                    logging.warning("量化二-期货保证金分析文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化二-结算数据-三、保证金使用情况设置 单元格时发生错误: {e}")                  
                                    
            ################# 四、交易情况;
            try:
                if self.src_dict_['量化二']['成交回报'] is not None:
                    set_value(sheet, self.sheet3_dict_['交易方向及数量'].row_, 2,'future_info_2', self.src_dict_['量化二']['成交回报'], '量化二-成交回报', False, self.border_)
                else:
                    logging.warning("量化二-成交回报文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化二-结算数据-四、交易情况 单元格时发生错误: {e}")         
                             
            ################# 五、持仓情况;
            try:
                if self.src_dict_['量化二']['汇总证券-当日持仓'] is not None:
                    set_value(sheet, self.sheet3_dict_['持仓品种及数量'].row_,2,'future_info_2', self.src_dict_['量化二']['汇总证券-当日持仓'], '量化二-汇总证券-当日持仓', False, self.border_)
                else:
                    logging.warning("量化二-汇总证券-当日持仓文件不存在。")           
            except Exception as e:
                logging.error(f"生成 量化二-结算数据-五、持仓情况 单元格时发生错误: {e}")
                                                
                                            
            set_sheet_middle(sheet)

            ################# 样式设置;
            try:
                sheet.column_dimensions['A'].width = 44
                sheet.column_dimensions['B'].width = 58 

                for key, excel_data in self.sheet3_dict_.items():
                    if key == '交易方向及数量' or key == '持仓品种及数量':
                        sheet.row_dimensions[excel_data.row_].height = 140 
                    elif key == '注释':
                        sheet.row_dimensions[excel_data.row_].height = 60
                    else:
                        sheet.row_dimensions[excel_data.row_].height = 27
                
                sheet.cell(row = self.sheet3_dict_['交易方向及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
                sheet.cell(row = self.sheet3_dict_['交易方向及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
                sheet.cell(row = self.sheet3_dict_['持仓品种及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
                sheet.cell(row = self.sheet3_dict_['持仓品种及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                
                for key, value in self.sheet3_dict_.items():
                    if is_merge_all(key):
                        sheet.merge_cells(start_row=value.row_, start_column=1, end_row=value.row_, end_column=cell_count)
                    else:
                        sheet.merge_cells(start_row=value.row_, start_column=2, end_row=value.row_, end_column=cell_count)    
                    
                self.jz_['量化二']['结算数据'].draw_chart(self.draw_line_days_, self.file_path_, 
                                                        self.draw_net_value_curve_, sheet, '量化二-结算数据')  
            except Exception as e:
                logging.error(f"生成 量化二-结算数据-最后样式设计 单元格时发生错误: {e}")    
                
            self.gene_sheet_array_.append('量化二-结算数据')                
                                                                            
        except Exception as e:
            logging.error(f"生成 量化二-结算数据 表格时发生错误: {e}")
                
    def gene_fourth_sheet(self):
        try:
            ################# 基础信息设置
            try:
                item_array = [
                            '统计日期', 
                            '一、账户资产及收益情况', '账户名称', '账户编号', '资产单元名称', '账户资产净值', '返息', '手续费','总盈利/亏损(含返息、手续费)', '收益率(含返息、手续费)', '总盈利/亏损(不含返息、手续费)', '收益率(不含返息、手续费)',
                            '二、净值列示', '实收资本', '资产净值', '总份额', '期初单位净值', '昨日单位净值(含返息、手续费)', '单位净值(含返息、手续费)', '日净值增长率(含返息、手续费)','昨日单位净值(不含返息、手续费)', '单位净值(不含返息、手续费)', '日净值增长率(不含返息、手续费)',
                            '三、保证金使用情况', '占用', '账户权益', '风险度',
                            '四、交易情况', '交易方向及数量',
                            '五、持仓情况', '持仓品种及数量']
                sheet = self.target_workbook_.create_sheet(title='量化二-收盘数据')
                
                tmp_index = 1
                for item in item_array:
                    self.sheet4_dict_[item] = ExcelData(row = tmp_index)
                    tmp_index += 1     
                                    
                self.set_sheet_font(sheet, self.sheet4_dict_, '量化二-收盘数据')
                                                                                            
                sheet.cell(row = self.sheet4_dict_['一、账户资产及收益情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet4_dict_['二、净值列示'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet4_dict_['三、保证金使用情况'].row_, column = 1).fill = self.fill_  #问题
                sheet.cell(row = self.sheet4_dict_['四、交易情况'].row_, column = 1).fill = self.fill_        
                sheet.cell(row = self.sheet4_dict_['五、持仓情况'].row_, column = 1).fill = self.fill_
            
            except Exception as e:
                logging.error(f"生成 量化二-收盘数据-基础信息设置 单元格时发生错误: {e}")             
                    
            this_date = None
            ################# 一、账户资产及收益情况 相关设置;    
            try:                
                cell_count = 1             
                cell_col_index = {}
                self.sheet4_dict_['资产净值'].value_ = 0
                if self.src_dict_['量化二']['单元资产'] is not None:
                    cell_index = 1
                    for key, value in self.src_dict_['量化二']['单元资产'].items():
                        if key != '合计':
                        
                            dt = datetime.strptime(value['统计日期'], '%Y-%m-%d')
                            this_date = dt.strftime('%Y-%m-%d')
                            self.date = this_date
                                                        
                            sheet.cell(row = self.sheet4_dict_['统计日期'].row_, column = 2, value=str(value['统计日期']) + ", (金额单位：元)")
                            set_value(sheet, self.sheet4_dict_['账户名称'].row_,2,'账户名称', value, '量化二-单元资产', False, self.border_)
                            tmpzhbh = value['账户编号']
                            sheet.cell(row = self.sheet4_dict_['账户编号'].row_, column = 2, value=math.floor(float(tmpzhbh)))
                            sheet.cell(row = self.sheet4_dict_['账户编号'].row_, column = 2).border = self.border_
                            set_value(sheet, self.sheet4_dict_['资产单元名称'].row_,1+cell_index,'资产单元名称', value, '量化二-单元资产', False, self.border_)
                            if '投机单元' not in key:
                                set_value(sheet, self.sheet4_dict_['账户资产净值'].row_,1+cell_index,'单元资产净值(净价)', value, '量化二-单元资产', False,self.border_)
                                self.sheet4_dict_['资产净值'].value_ = float(value['单元资产净值(净价)'])
                            else:
                                sheet.cell(row = self.sheet4_dict_['账户资产净值'].row_, column = 2, value=self.src_dict_['量化二']['手动输入数据']['账户资产净值']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户资产净值 = 【手动输入】
                                sheet.cell(row = self.sheet4_dict_['账户资产净值'].row_, column = 2).border = self.border_
                                self.sheet4_dict_['资产净值'].value_ = self.src_dict_['量化二']['手动输入数据']['账户资产净值']
                            
                            sheet.cell(row = self.sheet4_dict_['返息'].row_, column = 2, value=self.src_dict_['量化二']['手动输入数据']['返息'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet4_dict_['返息'].row_, column = 2).border = self.border_     


                            sheet.cell(row = self.sheet4_dict_['手续费'].row_, column = 2, value=self.src_dict_['量化二']['手动输入数据']['手续费'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet4_dict_['手续费'].row_, column = 2).border = self.border_                                
                                                        
                            self.sheet4_dict_['总盈利/亏损(含返息、手续费)'].value_ = self.sheet4_dict_['资产净值'].value_ - self.src_dict_['量化二']['手动输入数据']['实收资本']
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2, value=self.sheet4_dict_['总盈利/亏损(含返息、手续费)'].value_ ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                            
                            self.sheet4_dict_['收益率(含返息、手续费)'].value_ = self.sheet4_dict_['总盈利/亏损(含返息、手续费)'].value_  / self.src_dict_['量化二']['手动输入数据']['实收资本'] * 100 # 收益率 = (账户资产净值 - 1000万元)÷1000万元×100%【保留4位小数】
                            sheet.cell(row = self.sheet4_dict_['收益率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet4_dict_['收益率(含返息、手续费)'].value_ , 4))+"%")
                            sheet.cell(row = self.sheet4_dict_['收益率(含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet4_dict_['收益率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                            sheet.cell(row = self.sheet4_dict_['收益率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                            
                            self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].value_ = self.sheet4_dict_['资产净值'].value_ - self.src_dict_['量化二']['手动输入数据']['实收资本'] - self.src_dict_['量化二']['手动输入数据']['返息'] - self.src_dict_['量化二']['手动输入数据']['手续费']
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2, value=self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].value_ ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                            sheet.cell(row = self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                            
                            self.sheet4_dict_['收益率(不含返息、手续费)'].value_ = self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].value_  / self.src_dict_['量化二']['手动输入数据']['实收资本'] * 100 # 收益率 = (账户资产净值 - 1000万元)÷1000万元×100%【保留4位小数】
                            sheet.cell(row = self.sheet4_dict_['收益率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet4_dict_['收益率(不含返息、手续费)'].value_ , 4))+"%")
                            sheet.cell(row = self.sheet4_dict_['收益率(不含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet4_dict_['收益率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                            sheet.cell(row = self.sheet4_dict_['收益率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_                            
                            
                            cell_index += 1
                            cell_col_index[key] = cell_index    
                    # print(cell_col_index)
                    cell_count = cell_index
            
                else:
                    logging.warning("量化二-单元资产文件不存在。")
                    
            except Exception as e:
                logging.error(f"生成 量化二-收盘数据-一、账户资产及收益情况 单元格时发生错误: {e}")                  
                                   
                    
        
            ################# 二、净值列示设置  
            try:
                self.sheet4_dict_['实收资本'].value_ = self.src_dict_['量化二']['手动输入数据']['实收资本']
                
                
                sheet.cell(row = self.sheet4_dict_['实收资本'].row_, column = 2, value = self.sheet4_dict_['实收资本'].value_ ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet4_dict_['资产净值'].row_, column = 2, value = self.sheet4_dict_['资产净值'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                sheet.cell(row = self.sheet4_dict_['总份额'].row_, column = 2, value = self.src_dict_['量化二']['手动输入数据']['总份额']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet4_dict_['期初单位净值'].value_ = self.src_dict_['量化二']['手动输入数据']['实收资本'] / self.src_dict_['量化二']['手动输入数据']['总份额'] #期初单位净值
                sheet.cell(row = self.sheet4_dict_['期初单位净值'].row_, column = 2, value = round(self.sheet4_dict_['期初单位净值'].value_ , 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                                
                self.sheet4_dict_['昨日单位净值(含返息、手续费)'].value_ = self.jz_['量化二']['收盘数据'].last_jz_with_profit_
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet4_dict_['昨日单位净值(含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                
                self.sheet4_dict_['单位净值(含返息、手续费)'].value_ = self.sheet4_dict_['资产净值'].value_/self.src_dict_['量化二']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet4_dict_['单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet4_dict_['单位净值(含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet4_dict_['单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet4_dict_['单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet4_dict_['单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                
                self.sheet4_dict_['日净值增长率(含返息、手续费)'].value_ = (self.sheet4_dict_['单位净值(含返息、手续费)'].value_ - self.sheet4_dict_['昨日单位净值(含返息、手续费)'].value_) / self.sheet4_dict_['昨日单位净值(含返息、手续费)'].value_ * 100
                sheet.cell(row = self.sheet4_dict_['日净值增长率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet4_dict_['日净值增长率(含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet4_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).border = self.border_   
                sheet.cell(row = self.sheet4_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_   
                sheet.cell(row = self.sheet4_dict_['日净值增长率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_   
                
                self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].value_ = self.jz_['量化二']['收盘数据'].last_jz_no_profit_
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                self.sheet4_dict_['单位净值(不含返息、手续费)'].value_ = (self.sheet4_dict_['实收资本'].value_ +  self.sheet4_dict_['总盈利/亏损(不含返息、手续费)'].value_) / self.src_dict_['量化二']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet4_dict_['单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet4_dict_['单位净值(不含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet4_dict_['单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet4_dict_['单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet4_dict_['单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                self.sheet4_dict_['日净值增长率(不含返息、手续费)'].value_ = (self.sheet4_dict_['单位净值(不含返息、手续费)'].value_ - self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].value_) / self.sheet4_dict_['昨日单位净值(不含返息、手续费)'].value_ * 100
                sheet.cell(row = self.sheet4_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet4_dict_['日净值增长率(不含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet4_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).border = self.border_   
                sheet.cell(row = self.sheet4_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_   
                sheet.cell(row = self.sheet4_dict_['日净值增长率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_                  
                
                
                sheet.cell(row = self.sheet4_dict_['实收资本'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet4_dict_['资产净值'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet4_dict_['总份额'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet4_dict_['期初单位净值'].row_, column = 2).border = self.border_
                
                self.jz_['量化二']['收盘数据'].update_data(this_date, 
                                                        self.sheet4_dict_['单位净值(含返息、手续费)'].value_, 
                                                        self.sheet4_dict_['单位净值(不含返息、手续费)'].value_)       
            except Exception as e:
                logging.error(f"生成 量化二-收盘数据-二、净值列示设置 单元格时发生错误: {e}")                    
                
            ################# 三、保证金使用情况设置;
            try:
                if self.src_dict_['量化二']['期货保证金分析'] is not None:
                    for key, value in self.src_dict_['量化二']['期货保证金分析'].items():
                        if key in cell_col_index:   
                            sheet.cell(row = self.sheet4_dict_['账户权益'].row_, column = cell_col_index[key], value=self.src_dict_['量化二']['手动输入数据']['账户资产净值']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 账户资产净值
                            sheet.cell(row = self.sheet4_dict_['账户权益'].row_, column = cell_col_index[key]).border = self.border_

                            self.sheet4_dict_['占用'].value_ = value['占用保证金(静态)']
                            sheet.cell(row = self.sheet4_dict_['占用'].row_, column = cell_col_index[key], value=self.sheet4_dict_['占用'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 占用 = 手动输入
                            sheet.cell(row = self.sheet4_dict_['占用'].row_, column = cell_col_index[key]).border = self.border_

                            
                            self.sheet4_dict_['风险度'].value_ = self.sheet4_dict_['占用'].value_ / self.src_dict_['量化二']['手动输入数据']['账户资产净值']*100 # 风险度 = 占用÷账户权益×100%【保留4位小数】
                            sheet.cell(row = self.sheet4_dict_['风险度'].row_, column = cell_col_index[key], value= str(round( self.sheet4_dict_['风险度'].value_, 4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 
                            sheet.cell(row = self.sheet4_dict_['风险度'].row_, column = cell_col_index[key]).border = self.border_
                        else:
                            logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                else:
                    logging.warning("量化二-期货保证金分析文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化二-收盘数据-三、保证金使用情况设置 单元格时发生错误: {e}")                  
                                
            ################# 四、交易情况;
            if self.src_dict_['量化二']['成交回报'] is not None:
                set_value(sheet, self.sheet4_dict_['交易方向及数量'].row_,2,'future_info_2', self.src_dict_['量化二']['成交回报'], '量化二-成交回报',False,self.border_)
            else:
                logging.warning("量化二-成交回报文件不存在。")
                
            ################# 五、持仓情况;
            if self.src_dict_['量化二']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet4_dict_['持仓品种及数量'].row_,2,'future_info_2', self.src_dict_['量化二']['汇总证券-当日持仓'], '量化二-汇总证券-当日持仓', False, self.border_)
            else:
                logging.warning("量化二-汇总证券-当日持仓文件不存在。")             
            # sheet.cell(row = self.sheet4_dict_['注释'], column = 1, value = '注：交易情况中的商品期货数量未去重。')
                                
            set_sheet_middle(sheet)

            ################# 样式设置;
            try:
                sheet.column_dimensions['A'].width = 44
                # 设置第二列(B列)的宽度为10个字符
                sheet.column_dimensions['B'].width = 58     

                for key, excel_data in self.sheet4_dict_.items():
                    if key == '交易方向及数量' or key == '持仓品种及数量':
                        sheet.row_dimensions[excel_data.row_].height = 140 
                    elif key == '注释':
                        sheet.row_dimensions[excel_data.row_].height = 60
                    else:
                        sheet.row_dimensions[excel_data.row_].height = 27
                
                sheet.cell(row = self.sheet4_dict_['交易方向及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
                sheet.cell(row = self.sheet4_dict_['交易方向及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
                sheet.cell(row = self.sheet4_dict_['持仓品种及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
                sheet.cell(row = self.sheet4_dict_['持仓品种及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                    
                for key, excel_data in self.sheet4_dict_.items():
                    if is_merge_all(key):
                        sheet.merge_cells(start_row=excel_data.row_, start_column=1, end_row=excel_data.row_, end_column=cell_count)
                    else:
                        sheet.merge_cells(start_row=excel_data.row_, start_column=2, end_row=excel_data.row_, end_column=cell_count)        

                self.jz_['量化二']['收盘数据'].draw_chart(self.draw_line_days_, self.file_path_, 
                                                        self.draw_net_value_curve_, sheet, '量化二-收盘数据')  
                        
            except Exception as e:
                logging.error(f"生成 量化二-收盘数据-最后样式设计 单元格时发生错误: {e}")             
                
            self.gene_sheet_array_.append('量化二-收盘数据')   
        except Exception as e:
            logging.error(f"生成 量化二-收盘数据 表格时发生错误: {e}")

    def gene_fivth_sheet(self):
        try:
            try:
                item_arrary = ['统计日期', 
                            '一、账户资产及收益情况', '账户名称', '账户编号', '资产单元名称', '账户资产净值', '返息', '手续费',
                                    '总盈利/亏损(含返息、手续费)', '收益率(含返息、手续费)', '总盈利/亏损(不含返息、手续费)', '收益率(不含返息、手续费)', 
                            '二、净值列示', '实收资本', '资产净值', '总份额', '期初单位净值', 
                                    '昨日单位净值(含返息、手续费)', '单位净值(含返息、手续费)', '日净值增长率(含返息、手续费)', 
                                    '昨日单位净值(不含返息、手续费)', '单位净值(不含返息、手续费)', '日净值增长率(不含返息、手续费)', 
                            '三、保证金使用情况', '占用', '账户权益', '风险度', 
                            '四、交易情况', '交易方向及数量', 
                            '五、持仓情况', '持仓品种及数量']
                
                tmp_index = 1
                for item in item_arrary:
                    self.sheet5_dict_[item] = ExcelData(row = tmp_index)
                    tmp_index += 1
                                                    
                sheet = self.target_workbook_.create_sheet(title='量化三-结算数据')
                
                self.set_sheet_font(sheet, self.sheet5_dict_, '量化三-结算数据')
                                                        
                sheet.cell(row = self.sheet5_dict_['一、账户资产及收益情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet5_dict_['二、净值列示'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet5_dict_['三、保证金使用情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet5_dict_['四、交易情况'].row_, column = 1).fill = self.fill_        
                sheet.cell(row = self.sheet5_dict_['五、持仓情况'].row_, column = 1).fill = self.fill_
            except Exception as e:
                logging.error(f"生成 量化三-结算数据-基础信息设置 单元格时发生错误: {e}")             
                            
            this_date = None
            ################# 一、账户资产及收益情况 相关设置;        
            try:
                cell_count = 1             
                cell_col_index = {}
                self.sheet5_dict_['账户资产净值'].value_  = 0
                if self.src_dict_['量化三']['单元资产'] is not None:
                    cell_index = 1
                    for key, value in self.src_dict_['量化三']['单元资产'].items():
                        if key != '合计':
                            dt = datetime.strptime(value['统计日期'], '%Y-%m-%d')
                            this_date = dt.strftime('%Y-%m-%d')
                            self.date = this_date
                                                        
                            sheet.cell(row = self.sheet5_dict_['统计日期'].row_, column = 2, value=str(value['统计日期']) + ", (金额单位：元)").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            set_value(sheet, self.sheet5_dict_['账户名称'].row_,2,'账户名称', value, '量化三-单元资产', False,self.border_)
                            tmpzhbh = value['账户编号']
                            sheet.cell(row = self.sheet5_dict_['账户编号'].row_, column = 2, value=math.floor(float(tmpzhbh)))
                            sheet.cell(row = self.sheet5_dict_['账户编号'].row_, column = 2).border = self.border_
                            set_value(sheet, self.sheet5_dict_['资产单元名称'].row_,1+cell_index,'资产单元名称', value, '量化三-单元资产', False, self.border_)
                            
                            self.sheet5_dict_['账户资产净值'].value_ = float(value['单元资产净值(净价)'])
                            set_value(sheet, self.sheet5_dict_['账户资产净值'].row_,1+cell_index,'单元资产净值(净价)', value, '量化三-单元资产', True, self.border_)
                            
                            sheet.cell(row = self.sheet5_dict_['返息'].row_, column = 2, value=self.src_dict_['量化三']['手动输入数据']['返息'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet5_dict_['返息'].row_, column = 2).border = self.border_           
                            
                            sheet.cell(row = self.sheet5_dict_['手续费'].row_, column = 2, value=self.src_dict_['量化三']['手动输入数据']['手续费'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet5_dict_['手续费'].row_, column = 2).border = self.border_                                                    
                                                                                    
                            cell_index += 1
                            cell_col_index[key] = cell_index    
                    # print(cell_col_index)
                    cell_count = cell_index
            
                else:
                    logging.warning("量化三-单元资产文件不存在。")
                        
                profits1 = 0  #总盈利/亏损(不含返息、逆回购、手续费)
                if self.src_dict_['量化三']['汇总证券-合计'] is not None:
                    if 'profit' in self.src_dict_['量化三']['汇总证券-合计']:
                        profits1 = self.src_dict_['量化三']['汇总证券-合计']['profit']
                        
                        self.sheet5_dict_['总盈利/亏损(含返息、手续费)'].value_ = self.sheet5_dict_['账户资产净值'].value_  -  self.src_dict_['量化三']['手动输入数据']['实收资本']
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2, value = round(self.sheet5_dict_['总盈利/亏损(含返息、手续费)'].value_ ,4)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 与量化二不同的地方;
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                        
                        self.sheet5_dict_['收益率(含返息、手续费)'].value_ = self.sheet5_dict_['总盈利/亏损(含返息、手续费)'].value_  / self.src_dict_['量化三']['手动输入数据']['实收资本'] * 100
                        sheet.cell(row = self.sheet5_dict_['收益率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet5_dict_['收益率(含返息、手续费)'].value_,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet5_dict_['收益率(含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet5_dict_['收益率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                        sheet.cell(row = self.sheet5_dict_['收益率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                        
                        self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].value_ = self.sheet5_dict_['账户资产净值'].value_  - self.src_dict_['量化三']['手动输入数据']['实收资本'] - self.src_dict_['量化三']['手动输入数据']['返息'] - self.src_dict_['量化三']['手动输入数据']['手续费']
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2, value = round(self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].value_,4)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                        sheet.cell(row = self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                        
                        self.sheet5_dict_['收益率(不含返息、手续费)'].value_ = (self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].value_) / self.src_dict_['量化三']['手动输入数据']['实收资本'] * 100 #收益率
                        sheet.cell(row = self.sheet5_dict_['收益率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet5_dict_['收益率(不含返息、手续费)'].value_,4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                        sheet.cell(row = self.sheet5_dict_['收益率(不含返息、手续费)'].row_, column = 2).border = self.border_
                        sheet.cell(row = self.sheet5_dict_['收益率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_ 
                        sheet.cell(row = self.sheet5_dict_['收益率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_  
                                                
                    else:
                        logging.warning("量化三-汇总证券-合计文件不存在。")
                else:
                    logging.warning("量化三-汇总证券-合计文件不存在。")
                    
            except Exception as e:
                logging.error(f"生成 量化三-结算数据-一、账户资产及收益情况 单元格时发生错误: {e}")                       
                    
            ################# 二、净值列示设置  
            try:                                  
                self.sheet5_dict_['实收资本'].value_ = self.src_dict_['量化三']['手动输入数据']['实收资本']
                sheet.cell(row = self.sheet5_dict_['实收资本'].row_, column = 2, value = self.sheet5_dict_['实收资本'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet5_dict_['资产净值'].value_ = self.sheet5_dict_['账户资产净值'].value_
                sheet.cell(row = self.sheet5_dict_['资产净值'].row_, column = 2, value = self.sheet5_dict_['资产净值'].value_ ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            
                sheet.cell(row = self.sheet5_dict_['总份额'].row_, column = 2, value = self.src_dict_['量化三']['手动输入数据']['总份额']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet5_dict_['期初单位净值'].value_ = self.sheet5_dict_['实收资本'].value_ /self.src_dict_['量化三']['手动输入数据']['总份额'] #期初单位净值
                sheet.cell(row = self.sheet5_dict_['期初单位净值'].row_, column = 2, value = round(self.sheet5_dict_['期初单位净值'].value_, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                
                self.sheet5_dict_['昨日单位净值(含返息、手续费)'].value_ = self.jz_['量化三']['结算数据'].last_jz_with_profit_
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet5_dict_['昨日单位净值(含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                                
                self.sheet5_dict_['单位净值(含返息、手续费)'].value_ = self.sheet5_dict_['账户资产净值'].value_ /self.src_dict_['量化三']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet5_dict_['单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet5_dict_['单位净值(含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet5_dict_['单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet5_dict_['单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet5_dict_['单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                                
                self.sheet5_dict_['日净值增长率(含返息、手续费)'].value_ = (self.sheet5_dict_['单位净值(含返息、手续费)'].value_ - self.sheet5_dict_['昨日单位净值(含返息、手续费)'].value_) / self.sheet5_dict_['昨日单位净值(含返息、手续费)'].value_ * 100 #日净值增长率
                sheet.cell(row = self.sheet5_dict_['日净值增长率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet5_dict_['日净值增长率(含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet5_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).border = self.border_ 
                sheet.cell(row = self.sheet5_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_ 
                sheet.cell(row = self.sheet5_dict_['日净值增长率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_ 
                

                self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].value_ = self.jz_['量化三']['结算数据'].last_jz_no_profit_
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                self.sheet5_dict_['单位净值(不含返息、手续费)'].value_ = (self.sheet5_dict_['实收资本'].value_ +  self.sheet5_dict_['总盈利/亏损(不含返息、手续费)'].value_) / self.src_dict_['量化三']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet5_dict_['单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet5_dict_['单位净值(不含返息、手续费)'].value_ , 5))
                sheet.cell(row = self.sheet5_dict_['单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet5_dict_['单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet5_dict_['单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                
                self.sheet5_dict_['日净值增长率(不含返息、手续费)'].value_ = (self.sheet5_dict_['单位净值(不含返息、手续费)'].value_  - self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].value_) / self.sheet5_dict_['昨日单位净值(不含返息、手续费)'].value_ * 100 #日净值增长率
                sheet.cell(row = self.sheet5_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet5_dict_['日净值增长率(不含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet5_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).border = self.border_ 
                sheet.cell(row = self.sheet5_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_ 
                sheet.cell(row = self.sheet5_dict_['日净值增长率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_  
                                
                                                    
                sheet.cell(row = self.sheet5_dict_['实收资本'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet5_dict_['资产净值'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet5_dict_['总份额'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet5_dict_['期初单位净值'].row_, column = 2).border = self.border_
                
                self.jz_['量化三']['结算数据'].update_data(this_date, 
                                                        self.sheet5_dict_['单位净值(含返息、手续费)'].value_, 
                                                        self.sheet5_dict_['单位净值(不含返息、手续费)'].value_)                  
                                
            except Exception as e:
                logging.error(f"生成 量化三-结算数据-二、净值列示设置 单元格时发生错误: {e}")   
                                
            ################# 三、保证金使用情况设置;
            try:
                if self.src_dict_['量化三']['期货保证金分析'] is not None:
                    for key, value in self.src_dict_['量化三']['期货保证金分析'].items():
                        if key in cell_col_index:
                            set_value(sheet, self.sheet5_dict_['占用'].row_,cell_col_index[key],'占用保证金(静态)', value, '量化三-期货保证金分析', True, self.border_)
                            set_value(sheet, self.sheet5_dict_['账户权益'].row_,cell_col_index[key],'账户权益', value, '量化三-期货保证金分析', True, self.border_)
                            sheet.cell(row = self.sheet5_dict_['风险度'].row_, column = cell_col_index[key], value = str(round(float(value['风险比例1(%)']),4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            sheet.cell(row = self.sheet5_dict_['风险度'].row_, column = cell_col_index[key]).border = self.border_
                        else:
                            logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                else:
                    logging.warning("量化三-期货保证金分析文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化三-结算数据-三、保证金使用情况设置 单元格时发生错误: {e}")        
                
                                    
            ################# 四、交易情况;
            try:
                if self.src_dict_['量化三']['成交回报'] is not None:
                    set_value(sheet, self.sheet5_dict_['交易方向及数量'].row_,2,'future_info', self.src_dict_['量化三']['成交回报'], '量化三-成交回报', False, self.border_)  # 不同的地方
                else:
                    logging.warning("量化三-成交回报文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化三-结算数据-四、交易情况 单元格时发生错误: {e}")                      
                
            ################# 五、持仓情况;
            try:
                if self.src_dict_['量化三']['汇总证券-当日持仓'] is not None:
                    set_value(sheet, self.sheet5_dict_['持仓品种及数量'].row_,2,'future_info', self.src_dict_['量化三']['汇总证券-当日持仓'], '量化三-汇总证券-当日持仓', False, self.border_) # 不同的地方
                else:
                    logging.warning("量化三-汇总证券-当日持仓文件不存在。")        
            except Exception as e:
                logging.error(f"生成 量化三-结算数据-五、持仓情况 单元格时发生错误: {e}")                         
                                    
            # sheet.cell(row = self.sheet5_dict_['注释'], column = 1, value = '注：交易情况中的商品期货数量未去重。')
                            
            ################# 样式设置;
            try:
                set_sheet_middle(sheet)

                sheet.column_dimensions['A'].width = 44
                sheet.column_dimensions['B'].width = 58 

                for key, excel_data in self.sheet5_dict_.items():
                    if key == '交易方向及数量' or key == '持仓品种及数量':
                        sheet.row_dimensions[excel_data.row_].height = 140 
                    elif key == '注释':
                        sheet.row_dimensions[excel_data.row_].height = 60
                    else:
                        sheet.row_dimensions[excel_data.row_].height = 27
                
                sheet.cell(row = self.sheet5_dict_['交易方向及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
                sheet.cell(row = self.sheet5_dict_['交易方向及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
                sheet.cell(row = self.sheet5_dict_['持仓品种及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
                sheet.cell(row = self.sheet5_dict_['持仓品种及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                # sheet.cell(row = self.sheet5_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                
                for key, value in self.sheet5_dict_.items():
                    if is_merge_all(key):
                        sheet.merge_cells(start_row=value.row_, start_column=1, end_row=value.row_, end_column=cell_count)
                    else:
                        sheet.merge_cells(start_row=value.row_, start_column=2, end_row=value.row_, end_column=cell_count)  
                    
                self.jz_['量化三']['结算数据'].draw_chart(self.draw_line_days_, self.file_path_, 
                                                        self.draw_net_value_curve_, sheet, '量化三-结算数据')  
                
            except Exception as e:
                logging.error(f"生成 量化三-结算数据-最后样式设计 单元格时发生错误: {e}")                   

            # logging.info(self.all_jz_3_1_['unit_net_value'])
            
            self.gene_sheet_array_.append('量化三-结算数据')   

        except Exception as e:
            logging.error(f"生成 量化三-结算数据 表格时发生错误: {e}")
                
    def gene_sixth_sheet(self):
        try:
            try:
                item_array = ['统计日期', 
                            '一、账户资产及收益情况', '账户名称', '账户编号', '资产单元名称', '账户资产净值', '返息', '手续费', 
                                '总盈利/亏损(含返息、手续费)', '收益率(含返息、手续费)', '总盈利/亏损(不含返息、手续费)', '收益率(不含返息、手续费)',
                            '二、净值列示', '实收资本', '资产净值', '总份额', '期初单位净值', '昨日单位净值(含返息、手续费)', '单位净值(含返息、手续费)', 
                                '日净值增长率(含返息、手续费)','昨日单位净值(不含返息、手续费)', '单位净值(不含返息、手续费)', '日净值增长率(不含返息、手续费)',
                            '三、保证金使用情况', '占用', '账户权益', '风险度',
                            '四、交易情况', '交易方向及数量',
                            '五、持仓情况', '持仓品种及数量']
                                                    
                sheet = self.target_workbook_.create_sheet(title='量化三-收盘数据')
                
                tmp_index = 1
                for item in item_array:
                    self.sheet6_dict_[item] = ExcelData(row = tmp_index)
                    tmp_index += 1     
                                    
                self.set_sheet_font(sheet, self.sheet6_dict_, '量化三-收盘数据')
                                    
                sheet.cell(row = self.sheet6_dict_['一、账户资产及收益情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet6_dict_['二、净值列示'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet6_dict_['三、保证金使用情况'].row_, column = 1).fill = self.fill_
                sheet.cell(row = self.sheet6_dict_['四、交易情况'].row_, column = 1).fill = self.fill_        
                sheet.cell(row = self.sheet6_dict_['五、持仓情况'].row_, column = 1).fill = self.fill_
                        
            except Exception as e:
                logging.error(f"生成 量化三-收盘数据-基础信息设置 单元格时发生错误: {e}")    
                
            this_date = None
            ################# 一、账户资产及收益情况 相关设置;                    
            try:                        
                cell_count = 1             
                cell_col_index = {}
                zhzcjz = 0
                if self.src_dict_['量化三']['单元资产'] is not None:
                    cell_index = 1
                    for key, value in self.src_dict_['量化三']['单元资产'].items():
                        if key != '合计':
                            
                            dt = datetime.strptime(value['统计日期'], '%Y-%m-%d')
                            this_date = dt.strftime('%Y-%m-%d')
                            self.date = this_date
                                                        
                            sheet.cell(row = self.sheet6_dict_['统计日期'].row_, column = 2, value=str(value['统计日期']) + ", (金额单位：元)")
                            set_value(sheet, self.sheet6_dict_['账户名称'].row_,2,'账户名称', value, '量化三-单元资产', False, self.border_)
                            tmpzhbh = value['账户编号']
                            sheet.cell(row = self.sheet6_dict_['账户编号'].row_, column = 2, value=math.floor(float(tmpzhbh)))
                            sheet.cell(row = self.sheet6_dict_['账户编号'].row_, column = 2).border = self.border_
                            set_value(sheet, self.sheet6_dict_['资产单元名称'].row_,1+cell_index,'资产单元名称', value, '量化三-单元资产', False, self.border_)
                            
                            if '投机单元' not in key:
                                self.sheet6_dict_['账户资产净值'].value_ = float(value['单元资产净值(净价)'])
                                set_value(sheet, self.sheet6_dict_['账户资产净值'].row_,1+cell_index,'单元资产净值(净价)', value, '量化三-单元资产', False,self.border_)                                
                            else:
                                self.sheet6_dict_['账户资产净值'].value_ = self.src_dict_['量化三']['手动输入数据']['账户资产净值']
                                sheet.cell(row = self.sheet6_dict_['账户资产净值'].row_, column = 2, value=self.sheet6_dict_['账户资产净值'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户资产净值 = 【手动输入】
                                sheet.cell(row = self.sheet6_dict_['账户资产净值'].row_, column = 2).border = self.border_
                                
                            sheet.cell(row = self.sheet6_dict_['返息'].row_, column = 2, value=self.src_dict_['量化三']['手动输入数据']['返息'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet6_dict_['返息'].row_, column = 2).border = self.border_    
                            
                            sheet.cell(row = self.sheet6_dict_['手续费'].row_, column = 2, value=self.src_dict_['量化三']['手动输入数据']['手续费'] ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet6_dict_['手续费'].row_, column = 2).border = self.border_                                                            
                            
                            self.sheet6_dict_['总盈利/亏损(含返息、手续费)'].value_ = self.sheet6_dict_['账户资产净值'].value_  - self.src_dict_['量化三']['手动输入数据']['实收资本']  # 总盈利/亏损 = 账户资产净值 - 500w
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2, value=self.sheet6_dict_['总盈利/亏损(含返息、手续费)'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_                            
                            
                            self.sheet6_dict_['收益率(含返息、手续费)'].value_ = self.sheet6_dict_['总盈利/亏损(含返息、手续费)'].value_ / self.src_dict_['量化三']['手动输入数据']['实收资本'] * 100 # 收益率 = (账户资产净值 - 1000万元)÷1000万元×100%【保留4位小数】
                            sheet.cell(row = self.sheet6_dict_['收益率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet6_dict_['收益率(含返息、手续费)'].value_ , 4))+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            sheet.cell(row = self.sheet6_dict_['收益率(含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet6_dict_['收益率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                            sheet.cell(row = self.sheet6_dict_['收益率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                            
                            self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].value_ = self.sheet6_dict_['账户资产净值'].value_ - self.src_dict_['量化三']['手动输入数据']['实收资本'] - self.src_dict_['量化三']['手动输入数据']['返息'] - self.src_dict_['量化三']['手动输入数据']['手续费'] # 总盈利/亏损 = 账户资产净值 - 500w - 返息 - 手续费
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2, value=self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].value_ ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 总盈利/亏损 = 账户资产净值 - 1000万元【手动输入】
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                            sheet.cell(row = self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                            
                            self.sheet6_dict_['收益率(不含返息、手续费)'].value_ = self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].value_  / self.src_dict_['量化三']['手动输入数据']['实收资本'] * 100 # 收益率 = (账户资产净值 - 1000万元)÷1000万元×100%【保留4位小数】
                            sheet.cell(row = self.sheet6_dict_['收益率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet6_dict_['收益率(不含返息、手续费)'].value_ , 4))+"%")
                            sheet.cell(row = self.sheet6_dict_['收益率(不含返息、手续费)'].row_, column = 2).border = self.border_
                            sheet.cell(row = self.sheet6_dict_['收益率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                            sheet.cell(row = self.sheet6_dict_['收益率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_                                                               
                            
                            cell_index += 1
                            cell_col_index[key] = cell_index    
                    # print(cell_col_index)
                    cell_count = cell_index
            
                else:
                    logging.warning("量化三-单元资产文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化三-收盘数据-一、账户资产及收益情况 单元格时发生错误: {e}")                           
                    
        
            ################# 二、净值列示设置 
            try: 
                self.sheet6_dict_['实收资本'].value_ = self.src_dict_['量化三']['手动输入数据']['实收资本']
                sheet.cell(row = self.sheet6_dict_['实收资本'].row_, column = 2, value = self.sheet6_dict_['实收资本'].value_).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet6_dict_['资产净值'].value_ = self.sheet6_dict_['账户资产净值'].value_
                sheet.cell(row = self.sheet6_dict_['资产净值'].row_, column = 2, value = self.sheet6_dict_['资产净值'].value_ ).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                            
                sheet.cell(row = self.sheet6_dict_['总份额'].row_, column = 2, value = self.src_dict_['量化三']['手动输入数据']['总份额']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                self.sheet6_dict_['期初单位净值'].value_ = self.sheet6_dict_['实收资本'].value_ /self.src_dict_['量化三']['手动输入数据']['总份额'] #期初单位净值
                sheet.cell(row = self.sheet6_dict_['期初单位净值'].row_, column = 2, value = round(self.sheet6_dict_['期初单位净值'].value_, 5)).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1
                
                
                self.sheet6_dict_['昨日单位净值(含返息、手续费)'].value_ = self.jz_['量化三']['收盘数据'].last_jz_with_profit_
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet6_dict_['昨日单位净值(含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                                
                self.sheet6_dict_['单位净值(含返息、手续费)'].value_ = self.sheet6_dict_['账户资产净值'].value_ /self.src_dict_['量化三']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet6_dict_['单位净值(含返息、手续费)'].row_, column = 2, value = round(self.sheet6_dict_['单位净值(含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet6_dict_['单位净值(含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet6_dict_['单位净值(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_
                sheet.cell(row = self.sheet6_dict_['单位净值(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_
                                
                self.sheet6_dict_['日净值增长率(含返息、手续费)'].value_ = (self.sheet6_dict_['单位净值(含返息、手续费)'].value_ - self.sheet6_dict_['昨日单位净值(含返息、手续费)'].value_) / self.sheet6_dict_['昨日单位净值(含返息、手续费)'].value_ * 100 #日净值增长率
                sheet.cell(row = self.sheet6_dict_['日净值增长率(含返息、手续费)'].row_, column = 2, value = str(round(self.sheet6_dict_['日净值增长率(含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet6_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).border = self.border_ 
                sheet.cell(row = self.sheet6_dict_['日净值增长率(含返息、手续费)'].row_, column = 2).fill = self.with_profit_color_ 
                sheet.cell(row = self.sheet6_dict_['日净值增长率(含返息、手续费)'].row_, column = 1).fill = self.with_profit_color_ 
                

                self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].value_ = self.jz_['量化三']['收盘数据'].last_jz_no_profit_
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].value_, 5))
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                self.sheet6_dict_['单位净值(不含返息、手续费)'].value_ = (self.sheet6_dict_['实收资本'].value_ +  self.sheet6_dict_['总盈利/亏损(不含返息、手续费)'].value_) / self.src_dict_['量化三']['手动输入数据']['总份额'] #单位净值
                sheet.cell(row = self.sheet6_dict_['单位净值(不含返息、手续费)'].row_, column = 2, value = round(self.sheet6_dict_['单位净值(不含返息、手续费)'].value_ , 5))
                sheet.cell(row = self.sheet6_dict_['单位净值(不含返息、手续费)'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet6_dict_['单位净值(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_
                sheet.cell(row = self.sheet6_dict_['单位净值(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_
                
                
                self.sheet6_dict_['日净值增长率(不含返息、手续费)'].value_ = (self.sheet6_dict_['单位净值(不含返息、手续费)'].value_  - self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].value_) / self.sheet6_dict_['昨日单位净值(不含返息、手续费)'].value_ * 100 #日净值增长率
                sheet.cell(row = self.sheet6_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2, value = str(round(self.sheet6_dict_['日净值增长率(不含返息、手续费)'].value_, 5)) + '%')  
                sheet.cell(row = self.sheet6_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).border = self.border_ 
                sheet.cell(row = self.sheet6_dict_['日净值增长率(不含返息、手续费)'].row_, column = 2).fill = self.no_profit_color_ 
                sheet.cell(row = self.sheet6_dict_['日净值增长率(不含返息、手续费)'].row_, column = 1).fill = self.no_profit_color_  
                                
                                                    
                sheet.cell(row = self.sheet6_dict_['实收资本'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet6_dict_['资产净值'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet6_dict_['总份额'].row_, column = 2).border = self.border_
                sheet.cell(row = self.sheet6_dict_['期初单位净值'].row_, column = 2).border = self.border_
                
                self.jz_['量化三']['收盘数据'].update_data(this_date, 
                                                        self.sheet6_dict_['单位净值(含返息、手续费)'].value_, 
                                                        self.sheet6_dict_['单位净值(不含返息、手续费)'].value_)                  
                
            except Exception as e:
                logging.error(f"生成 量化三-收盘数据-二、净值列示设置 单元格时发生错误: {e}")   
                                                
            ################# 三、保证金使用情况设置;
            try: 
                if self.src_dict_['量化三']['期货保证金分析'] is not None:
                    for key, value in self.src_dict_['量化三']['期货保证金分析'].items():
                        if key in cell_col_index:   
                            sheet.cell(row = self.sheet6_dict_['账户权益'].row_, column = cell_col_index[key], value=self.src_dict_['量化三']['手动输入数据']['账户资产净值']).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 # 账户权益 = 账户资产净值
                            sheet.cell(row = self.sheet6_dict_['账户权益'].row_, column = cell_col_index[key]).border = self.border_
                            
                            self.sheet6_dict_['占用'].value_ = value['占用保证金(静态)']
                            set_value(sheet, self.sheet6_dict_['占用'].row_,cell_col_index[key],'占用保证金(静态)', value, '量化三-期货保证金分析', True, self.border_)
                            
                            self.sheet6_dict_['风险度'].value_ = round(self.sheet6_dict_['占用'].value_  / self.src_dict_['量化三']['手动输入数据']['账户资产净值'] * 100, 4) # 风险度 = 占用÷账户权益×100%【保留4位小数】
                            sheet.cell(row = self.sheet6_dict_['风险度'].row_, column = cell_col_index[key], value= str(self.sheet6_dict_['风险度'].value_)+"%").number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1 
                            sheet.cell(row = self.sheet6_dict_['风险度'].row_, column = cell_col_index[key]).border = self.border_                        

                        else:
                            logging.warning(f"期货保证金分析中的账户 {key} 不在单元资产中 ")
                else:
                    logging.warning("量化三-期货保证金分析文件不存在。")
            except Exception as e:
                logging.error(f"生成 量化三-收盘数据-三、保证金使用情况设置 单元格时发生错误: {e}")        
                            
                
            # logging.info(f"生成 量化三-成交回报: {self.src_dict_['量化三']['成交回报']['future_info']}")
            # logging.info(f"生成 量化三-成交回报: {self.src_dict_['量化三']['汇总证券-当日持仓']['future_info']}")
                                
            if self.src_dict_['量化三']['成交回报'] is not None:
                set_value(sheet, self.sheet6_dict_['交易方向及数量'].row_,2,'future_info', self.src_dict_['量化三']['成交回报'], '量化三-成交回报',False,self.border_)
            else:
                logging.warning("量化三-成交回报文件不存在。")
                
            if self.src_dict_['量化三']['汇总证券-当日持仓'] is not None:
                set_value(sheet, self.sheet6_dict_['持仓品种及数量'].row_,2,'future_info', self.src_dict_['量化三']['汇总证券-当日持仓'], '量化三-汇总证券-当日持仓', False, self.border_)
            else:
                logging.warning("量化三-汇总证券-当日持仓文件不存在。")             
                
                        
            set_sheet_middle(sheet)

            ################# 样式设置;
            try:
                sheet.column_dimensions['A'].width = 44
                # 设置第二列(B列)的宽度为10个字符
                sheet.column_dimensions['B'].width = 58     

                for key, excel_data in self.sheet6_dict_.items():
                    if key == '交易方向及数量' or key == '持仓品种及数量':
                        sheet.row_dimensions[excel_data.row_].height = 140 
                    elif key == '注释':
                        sheet.row_dimensions[excel_data.row_].height = 60
                    else:
                        sheet.row_dimensions[excel_data.row_].height = 27
                
                sheet.cell(row = self.sheet6_dict_['交易方向及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)   
                sheet.cell(row = self.sheet6_dict_['交易方向及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)                 
                sheet.cell(row = self.sheet6_dict_['持仓品种及数量'].row_, column = 2).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)
                sheet.cell(row = self.sheet6_dict_['持仓品种及数量'].row_, column = 3).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                # sheet.cell(row = self.sheet6_dict_['注释'], column = 1).alignment = Alignment(horizontal='left', vertical='center',wrap_text=True)    
                    
                for key, value in self.sheet6_dict_.items():
                    if is_merge_all(key):
                        sheet.merge_cells(start_row=value.row_, start_column=1, end_row=value.row_, end_column=cell_count)
                    else:
                        sheet.merge_cells(start_row=value.row_, start_column=2, end_row=value.row_, end_column=cell_count)  

                self.jz_['量化三']['收盘数据'].draw_chart(self.draw_line_days_, self.file_path_, 
                                                        self.draw_net_value_curve_, sheet, '量化三-收盘数据')  
            except Exception as e:
                logging.error(f"生成 量化三-收盘数据-最后样式设计 单元格时发生错误: {e}")   
                
            self.gene_sheet_array_.append('量化三-收盘数据')                   
                
        except Exception as e:
            logging.error(f"生成 量化三-收盘数据 表格时发生错误: {e}")

    def gene_seven_sheet(self):
        try:
            try:

                item_array = ['量化二持仓信息',  
                            '统计日期', '行业', '农副', '有色', '能化', '黑色', '贵金属', 
                            '股指期货', '其他', '合计', '汇总',
                            '风险度：', '权益：', '当日盈亏：', '总市值：', '去锁市值：', '平仓盈亏：']
                                                                    
                sheet = self.target_workbook_.create_sheet(title='量化二持仓信息')
                

                tmp_index = 1
                for item in item_array:
                    self.sheet7_dict_[item] = ExcelData(row = tmp_index)
                    tmp_index += 1     
                                    
                sheet.cell(row = self.sheet7_dict_['量化二持仓信息'].row_, column = 1, value = '量化二持仓信息').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['量化二持仓信息'].row_, column = 1, value = '量化二持仓信息')

                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 1, value = '行业').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 1, value = '行业').border = self.border_

                sheet.cell(row = self.sheet7_dict_['农副'].row_, column = 1, value = '农副').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['农副'].row_, column = 1, value = '农副').border = self.border_

                sheet.cell(row = self.sheet7_dict_['有色'].row_, column = 1, value = '有色').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['有色'].row_, column = 1, value = '有色').border = self.border_

                sheet.cell(row = self.sheet7_dict_['能化'].row_, column = 1, value = '黑色').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['能化'].row_, column = 1, value = '黑色').border = self.border_    

                sheet.cell(row = self.sheet7_dict_['黑色'].row_, column = 1, value = '黑色').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['黑色'].row_, column = 1, value = '黑色').border = self.border_    

                sheet.cell(row = self.sheet7_dict_['贵金属'].row_, column = 1, value = '贵金属').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['贵金属'].row_, column = 1, value = '贵金属').border = self.border_    

                sheet.cell(row = self.sheet7_dict_['股指期货'].row_, column = 1, value = '股指期货').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['股指期货'].row_, column = 1, value = '股指期货').border = self.border_    

                sheet.cell(row = self.sheet7_dict_['其他'].row_, column = 1, value = '其他').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['其他'].row_, column = 1, value = '其他').border = self.border_ 

                sheet.cell(row = self.sheet7_dict_['合计'].row_, column = 1, value = '合计').font = self.bold_font_
                sheet.cell(row = self.sheet7_dict_['合计'].row_, column = 1, value = '合计').border = self.border_   

                sheet.cell(row = self.sheet7_dict_['统计日期'].row_, column = 1, value = '统计日期')
                sheet.cell(row = self.sheet7_dict_['汇总'].row_, column = 1, value = '汇总')
                sheet.cell(row = self.sheet7_dict_['风险度：'].row_, column = 1, value = '风险度：')
                sheet.cell(row = self.sheet7_dict_['权益：'].row_, column = 1, value = '权益：')   
                sheet.cell(row = self.sheet7_dict_['当日盈亏：'].row_, column = 1, value = '当日盈亏：')    
                sheet.cell(row = self.sheet7_dict_['总市值：'].row_, column = 1, value = '总市值：')  
                sheet.cell(row = self.sheet7_dict_['去锁市值：'].row_, column = 1, value = '去锁市值：') 
                sheet.cell(row = self.sheet7_dict_['平仓盈亏：'].row_, column = 1, value = '平仓盈亏：')                      
                
                                                                                                                                            
                                                        
                sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)

                long_mk_fill = PatternFill(start_color='FADADE', end_color='FADADE', fill_type='solid')
                short_mk_fill = PatternFill(start_color='E3F2D9', end_color='E3F2D9', fill_type='solid')
                net_mk_fill = PatternFill(start_color='FFF4D1', end_color='FFF4D1', fill_type='solid')
                                    
                sheet.cell(row = self.sheet7_dict_['统计日期'].row_, column = 2, value = self.date)
                sheet.cell(row = self.sheet7_dict_['统计日期'].row_, column = 4, value = '单位：万元')

                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 2, value = '多头市值').border = self.border_
                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 2, value = '多头市值').font = self.bold_font_

                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 3, value = '空头市值').border = self.border_
                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 3, value = '空头市值').font = self.bold_font_

                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 4, value = '净市值').border = self.border_
                sheet.cell(row = self.sheet7_dict_['行业'].row_, column = 4, value = '净市值').font = self.bold_font_


                sheet.cell(row = self.sheet7_dict_['风险度：'].row_, column = 2, value = str(round(self.sheet3_dict_['风险度'].value_,4))+"%")
                sheet.cell(row = self.sheet7_dict_['权益：'].row_, column = 2, value = round(self.sheet3_dict_['账户资产净值'].value_/10000, 2))
                sheet.cell(row = self.sheet7_dict_['当日盈亏：'].row_, column = 2, value = round(self.src_dict_['量化二']['手动输入数据']['当日盈亏']/10000,2))   
                sheet.cell(row = self.sheet7_dict_['总市值：'].row_, column = 2, value = self.src_dict_['量化二']['其余信息']['结算数据']['总市值'])   
                sheet.cell(row = self.sheet7_dict_['去锁市值：'].row_, column = 2, value = round(self.src_dict_['量化二']['其余信息']['结算数据']['去锁市值']/10000,2))   
                sheet.cell(row = self.sheet7_dict_['平仓盈亏：'].row_, column = 2, value = round(self.src_dict_['量化二']['手动输入数据']['平仓盈亏']/10000,2))           
                        
            except Exception as e:
                logging.error(f"生成 量化三-收盘数据-基础信息设置 单元格时发生错误: {e}")    
                                
                        
            set_sheet_middle(sheet)

            ################# 样式设置;
            try:
                sheet.column_dimensions['A'].width = 15
                
                sheet.column_dimensions['B'].width = 20    

                sheet.column_dimensions['C'].width = 20   

                sheet.column_dimensions['D'].width = 20   

                # sheet.row_dimensions[excel_data.row_].height = 140  

                for industry_name in self.industry_list_:
                    sheet.cell(row = self.sheet7_dict_[industry_name].row_, column = 2, value= round(self.industry_dict_[industry_name]['统计数据']['多头市值'],2)).fill = long_mk_fill
                    sheet.cell(row = self.sheet7_dict_[industry_name].row_, column = 3, value= round(self.industry_dict_[industry_name]['统计数据']['空头市值'],2)).fill = short_mk_fill
                    sheet.cell(row = self.sheet7_dict_[industry_name].row_, column = 4, value= round(self.industry_dict_[industry_name]['统计数据']['净市值'],2)).fill = net_mk_fill
                    sheet.cell(row = self.sheet7_dict_[industry_name].row_, column = 2).border = self.border_
                    sheet.cell(row = self.sheet7_dict_[industry_name].row_, column = 3).border = self.border_
                    sheet.cell(row = self.sheet7_dict_[industry_name].row_, column = 4).border = self.border_
                
                
     


            except Exception as e:
                logging.error(f"生成 量化三-收盘数据-最后样式设计 单元格时发生错误: {e}")   
                
            # self.gene_sheet_array_.append('量化三-收盘数据')                   
            
            sheet_detail = self.target_workbook_.create_sheet(title='量化二持仓信息--详细统计')  
            copy_sheet(sheet, sheet_detail)         
            sheet_detail.column_dimensions['A'].width = 15
            sheet_detail.column_dimensions['B'].width = 20    
            sheet_detail.column_dimensions['C'].width = 20   
            sheet_detail.column_dimensions['D'].width = 20     
            sheet_detail.column_dimensions['E'].width = 60    
            sheet_detail.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)     
            
            # self.excel_industry_dict_['合计']['统计数据']['标的列表信息']  
            
            for industry_name in self.industry_list_:
                if industry_name != '合计':
                    sheet_detail.cell(row = self.sheet7_dict_[industry_name].row_, column = 5, value= self.industry_dict_[industry_name]['统计数据']['标的列表信息'])
        
            sheet_detail.cell(row = self.sheet7_dict_['去锁市值：'].row_, column = 5, value= self.industry_dict_['合计']['统计数据']['标的列表信息'])

        except Exception as e:
            logging.error(f"生成 量化三-收盘数据 表格时发生错误: {e}")            
               
if __name__ == "__main__":    
    excelobj = ExcelBase()

    dataReadObj= ExcelDataRead(excelobj.src_dict_, excelobj.industry_dict_)

    excelobj.InitDataDict(dataReadObj)

    excelobj.Work()
    input("请输入任意字符后按回车键退出程序...")
    sys.exit()