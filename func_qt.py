from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView, QScrollBar
from datetime import datetime

def update_tableinfo(table_view, message):
    if table_view != None:
        tablemodel = table_view.model()
        if tablemodel:
            msg_list = message.split("\n")
            if "" in msg_list:
                msg_list.remove("")
            for msg in msg_list:
                datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                row = tablemodel.rowCount()
                tablemodel.setItem(row, 0, QStandardItem(datetime_str))
                tablemodel.setItem(row, 1, QStandardItem(msg))
                ver_scrollbar = table_view.verticalScrollBar()
                ver_scrollbar.setSliderPosition(ver_scrollbar.maximum());

def update_tableinfo_with_rowdelta(table_view, message, row_delta):
    if table_view != None:
        tablemodel = table_view.model()
        if tablemodel:
            datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row = tablemodel.rowCount()
            if row < 3:
                index = row
            else:
                index = row + row_delta
                if index < 0:
                    index = 0

            print('index: ', index, 'row: ', row)
            tablemodel.setItem(index, 0, QStandardItem(datetime_str))
            tablemodel.setItem(index, 1, QStandardItem(message))
            ver_scrollbar = table_view.verticalScrollBar()
            ver_scrollbar.setSliderPosition(ver_scrollbar.maximum());