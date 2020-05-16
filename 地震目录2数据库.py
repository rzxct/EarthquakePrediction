from sys import argv
from datetime import datetime
import sqlite3

            
def 地震目录2数据库(地震目录名, 表名, 数据库名='地震目录.db'):
    create_sql = """create table %s(时间 DATETIME NOT NULL,纬度 DECIMAL(4,2) NOT NULL,经度 DECIMAL(5,2) NOT NULL,震级 DECIMAL(3,2) NOT NULL,深度 SMALLINT(3),地点 VARCHAR(50),
                    PRIMARY KEY(时间,纬度,经度))"""
    连接 = sqlite3.connect(数据库名)
    游标 = 连接.cursor()
    已存表 = [已存表[0] for 已存表 in 游标.execute('select name from sqlite_master where type="table"')]
    游标.execute("delete from %s" % 表名 if 表名 in 已存表 else create_sql % 表名)
    for 记录 in open(地震目录名, mode='rb'):
        try:
            记录 = 记录.decode('GBK')
            时间 = datetime.strptime(记录[1:15],"%Y%m%d%H%M%S")
            纬度 = float(记录[15:21])
            经度 = float(记录[21:28])
            震级 = float(记录[28:32])
            深度 = int(记录[32:35])
            地名 = 记录[39:].rstrip()
            游标.execute("insert into %s values(?,?,?,?,?,?)" % 表名, (时间,纬度,经度,震级,深度,地名))
        except Exception:
            pass
    连接.commit()
    连接.close()


if __name__ == '__main__':
    地震目录2数据库("HuaBei.EQT","华北")
    地震目录2数据库("china5.EQT","中国")
    地震目录2数据库("world7.EQT","全球")
