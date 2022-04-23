from methods import getMax
from areas import areas
from datetime import datetime

beg = input("请输入开始时间(YYYY-mm-dd HH:MM:SS):")
end = input("请输入结束时间(YYYY-mm-dd HH:MM:SS):")
for areaname, area in areas.items():
	maxes = getMax(area, (beg, end), "华北")
	print('%s\t发生的最大地震为:' % areaname)
	for 时间, 经度, 纬度, 地点, 震级 in maxes:
		print(时间.split(' ')[0], 地点, 震级)
