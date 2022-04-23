from areas import areas
from methods import getM_counts, GRfit,NB
from datetime import timedelta

for areaname, area in areas.items():
    M_counts = getM_counts(area, ['2000-01-01 00:00:00', '2020-12-31 00:00:00'], "华北")
    A, B, error = GRfit(M_counts)
    M, P = NB(A, B, timedelta(days = 365 * 20), timedelta(days = 365))
    print('明年 %s\t发生的最大地震最有可能的震级范围为:\tML %3.1f - %3.1f, 概率为%3.2f' % (areaname, M - 0.5, M + 0.5, P))
