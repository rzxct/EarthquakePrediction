from 地震预报库 import 获得最大地震
from 地震分区 import 地震分区
from datetime import datetime
if __name__ == '__main__':
    today = datetime.today()
    if today > datetime(today.year, 10, 1):
        today = datetime(today.year, 10, 1)
    elif today > datetime(today.year, 5, 1):
        today = datetime(today.year, 5, 1)
    else:
        today = datetime(today.year-1, 10, 1)
    before = datetime(today.year-1, today.month, today.day)
    for key, value in 地震分区.items():
        最大地震 = 获得最大地震(value, (before, today), "华北")
        print('去年 %s\t发生的最大地震为:' % key)
        for 时间, 经度, 纬度, 地点, 震级 in 最大地震:
            print(时间.split(' ')[0], 地点, 震级)
