import pandas as pd
from openpyxl import Workbook
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog


def create_excel_with_pandas():
    # 创建数据
    data = {
        'Column1': [1, 2, 3],
        'Column2': ['a', 'b', 'c'],
        'Column3': [4.5, 5.5, 6.5]
    }
    df = pd.DataFrame(data)

    # 将数据写入Excel文件
    df.to_excel('example_pandas.xlsx', index=False)



def create_excel_with_openpyxl():
    wb = Workbook()
    sheet = wb.active
    sheet.title = 'Sheet1'

    # 写入表头
    headers = ['Column1', 'Column2', 'Column3']
    for col_num, header in enumerate(headers, 1):
        sheet.cell(row = 1, column = col_num, value = header)

    # 写入数据
    data = [
        [1, 'a', 4.5],
        [2, 'b', 5.5],
        [3, 'c', 6.5]
    ]
    for row_num, row_data in enumerate(data, 2):
        for col_num, value in enumerate(row_data, 1):
            sheet.cell(row = row_num, column = col_num, value = value)

    wb.save('example_openpyxl.xlsx')
    



class FileDialogApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('文件选择对话框')
        self.setGeometry(100, 100, 800, 400)

        self.file_label = QLabel('未选择文件')
        select_button = QPushButton('选择文件')
        select_button.clicked.connect(self.select_file)

        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(select_button)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文件')
        if file_path:
            self.file_label.setText(file_path)

def test_dialog():
    app = QApplication(sys.argv)
    ex = FileDialogApp()
    ex.show()
    sys.exit(app.exec())  


if __name__ == "__main__":
    # create_excel_with_pandas()
    # create_excel_with_openpyxl()
    test_dialog()
