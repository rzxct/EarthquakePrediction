from 地震预报库 import SB
from 地震分区 import 地震分区
for 分区名, 空间范围 in 地震分区.items():
    平均震级 = SB(空间范围, "华北")
    print('明年 %s\t将会发生的最大地震为:\tML %3.1f - %3.1f' % (分区名, 平均震级-0.5, 平均震级+0.5))
