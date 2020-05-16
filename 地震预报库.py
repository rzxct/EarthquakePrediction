from datetime import date, datetime
from math import log, exp
from statistics import mean, variance
import sqlite3


def SB(空间范围, 表名):
    连接 = sqlite3.connect("地震目录.db")
    游标 = 连接.cursor()
    sql = 'select max(震级) from %s where 纬度>=%s and 纬度<=%s and 经度>=%s and 经度<=%s and ' % (表名, 空间范围[0], 空间范围[1], 空间范围[2], 空间范围[3]) + '时间>"%s" and 时间<="%s"'
    震级列表 = [tuple(游标.execute(sql % (date(year, 1, 1), date(year+1, 1, 1))))[0][0] for year in range(1970, date.today().year)]
    连接.close()
    return sum(震级列表)/len(震级列表)

def 获得时间最大震级字典(空间范围, 表名):
    连接 = sqlite3.connect("地震目录.db")
    游标 = 连接.cursor()
    sql = 'select max(震级) from %s where 纬度>=%s and 纬度<=%s and 经度>=%s and 经度<=%s and ' % (表名, 空间范围[0], 空间范围[1], 空间范围[2], 空间范围[3]) + '时间>"%s" and 时间<="%s"'
    T_Ms = {year: tuple(游标.execute(sql % (date(year, 1, 1), date(year+1, 1, 1))))[0][0] for year in range(1970, date.today().year)}
    连接.close()
    return T_Ms

def 获得最大地震(空间范围, 时间范围, 表名):
    连接 = sqlite3.connect("地震目录.db")
    游标 = 连接.cursor()
    范围 = '纬度>=%s and 纬度<=%s and 经度>=%s and 经度<=%s and 时间>"%s" and 时间<="%s"' % (空间范围[0], 空间范围[1], 空间范围[2], 空间范围[3], 时间范围[0], 时间范围[1])
    最大震级 = list(游标.execute('select max(震级) from %s where %s'% (表名, 范围)))[0][0]
    sql = 'select 时间,经度,纬度,地点,震级 from %s where %s and 震级>=%s'% (表名, 范围, 最大震级)
    最大地震 = list(游标.execute(sql))
    连接.close()
    return 最大地震

def NB(A, B):
    概率_震级 = {exp(-exp(A+B*(ml/10+0.5)))-exp(-exp(A+B*(ml/10-0.5))):ml/10 for ml in range(100)}
    return 概率_震级[max(概率_震级)]

def 获得震级概率字典(空间范围, 表名):
    连接 = sqlite3.connect("地震目录.db")
    游标 = 连接.cursor()
    时间 = (datetime.fromisoformat(tuple(游标.execute('select max(时间) from %s' % 表名))[0][0]) - datetime(1970,1,1)).total_seconds()/31556925.9747
    空间范围 = '纬度>=%s and 纬度<=%s and 经度>=%s and 经度<=%s' % (空间范围[0],空间范围[1],空间范围[2],空间范围[3])
    震级列表 = [ml[0] for ml in 游标.execute('select 震级 from %s where %s' % (表名, 空间范围))]
    连接.close()
    return {ml:log(num/时间) for ml,num in {i/10:len([ml for ml in 震级列表 if ml >= i/10]) for i in range(10, int(max(震级列表)*10))}.items() if num >=10}

def 最小二乘法拟合(字典):
    x均值, y均值 = mean(字典.keys()), mean(字典.values())
    B = sum((x-x均值)*(y-y均值) for x,y in 字典.items())/sum((x-x均值)**2 for x in 字典.keys())
    A = y均值 - B * x均值
    return A, B

def GR拟合(震级概率字典):
    while True:
        A, B = 最小二乘法拟合(震级概率字典)
        震级, 次数 = list(震级概率字典.keys()), list(震级概率字典.values())
        if 次数[0] < A+B*震级[0] and 次数[1] < A+B*震级[1] and A+B*震级[0]-次数[0] > A+B*震级[1]-次数[1]:
            震级概率字典.pop(震级[0])
        else:
            break
    return A, B
