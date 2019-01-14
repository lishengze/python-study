rm -fr dist/mainWindow/
pyinstaller mainWindow.py
cp -fr dist/plugins/ dist/scrapy/ dist/config.xlsx dist/WindPy.pth dist/mainWindow/