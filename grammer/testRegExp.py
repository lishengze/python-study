import re
str = "http://127.0.0.1:8000/chart.js"
# str = "chart.js"
reg_str = 'chart.js'
if re.match(reg_str, str):
	print 'Perfect match'
else:
	print 'Failed'

