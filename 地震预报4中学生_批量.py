from methods import 地震预报4中学生
from areas import areas

for areaname, area in areas.items():
    M_avg = 地震预报4中学生(area, (2000, 2021), "华北")
    print('明年 %s\t将会发生的最大地震为:\tML %3.1f - %3.1f' % (areaname, M_avg - 0.5, M_avg + 0.5))
