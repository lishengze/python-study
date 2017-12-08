import sys
from PyQt5.QtWidgets import QWidget, QApplication

def showWidget():
    app = QApplication(sys.argv)
    w = QWidget()
    w.show()
    w.setWindowTitle("Hello PyQt5")
    sys.exit(app.exec_())

def printInfo():
    print sys.executable

if __name__ == "__main__":
    showWidget()
    # printInfo()