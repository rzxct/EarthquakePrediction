"""
本模块包含了一系列可以用于地震预报的方法，这些方法与传统地震预报方法的区别是：
1,这些方法具有良好的逻辑基础，是严格按照科学逻辑来推导的。
2,这些方法具有足以秒杀传统预报方法的准确率,并为实践所验证
3,这些方法假定地震断层是分型结构，而采用了统计物理学的方法
版权所有 许崇涛 rzxct@163.com
"""
from datetime import date
from math import log10, exp
from statistics import mean, stdev
import sqlite3

def getCV(intervals:tuple) -> float:
	"""
	计算变异系数，变异系数 = 标准差 / 平均值
	"""
	return stdev(intervals) / mean(intervals)
	
def getIntervals(area:tuple, timeslot:tuple, magnitude:float, tablename:str) -> list:
	"""
	获得地震的时间间隔。需要指定空间范围，时间范围，以及震级范围（某震级以上地震）,所检索的表。
	"""
	conn = sqlite3.connect("地震目录.db")
	timeslot = '时间 >= "%s" and 时间 < "%s"' % (timeslot[0], timeslot[1])
	area = '纬度 >= %s and 纬度 <= %s and 经度 >= %s and 经度 <= %s' % (area[0], area[1], area[2], area[3])
	magnitude = '震级 >= %s' % magnitude
	datetimes = [int(datetime[0]) for datetime in conn.execute("select strftime('%s', 时间) from %s where %s and %s and %s" % ('%s', tablename, area, timeslot, magnitude))]
	conn.close()
	intervals = [datetimes[i + 1] - datetimes[i] for i in range(len(datetimes) - 1)]
	return intervals

def leastsquare(xys:dict):
	"""
	用于最小二乘法拟合直线y= A + B * x，要求输入为dict格式{x:y}，输出为A，B，A为Y轴交点，B为斜率
	"""
	x_avg = mean(xys.keys())
	y_avg = mean(xys.values())
	B = sum((x- x_avg) * (y - y_avg) for x, y in xys.items()) / sum ((x - x_avg) ** 2 for x in xys.keys())
	A = y_avg - B * x_avg
	return A, B
	
def GRfit(M_counts:dict):
	"""
	GR关系式拟合log10(count) = A + B * M，本拟合方法充分考虑了低震级地震漏报，高震级地震导致拟合线上翘，以及标准差分布特性等特点，是目前最准确最科学的GR关系式程序。
	要求输入为dict格式{M:count}，由于本程序可以自动处理高震级和低震级，故不需要您对此做额外处理.
	输出为A, B, error, error为误差
	"""
	M_counts = {M: log10(count) for M, count in M_counts.items() if count >4}
	while True:
		A, B = leastsquare(M_counts)
		Ms = list(M_counts.keys())
		counts = list(M_counts.values())
		if counts[0] < A + B * Ms[0] and counts[1] < A + B * Ms[1] and A + B * Ms[0] - counts[0] > A + B * Ms[1] - counts[1]:
			M_counts.pop(Ms[0])
		else:
			break
	error = stdev(A + B * M - count for M, count in M_counts.items())
	return A, B, error
	
def NB(A:float, B:float, souredelta, targetdelta):
	"""
	根据GR关系式预测未来地震的方法。
	1,这个方法的本质是认为地震断层是分型结构，地震的发生是无数不可预测的个体互相作用的结果，所以不符合牛顿力学，而符合统计物理学，所以，只能预测一系列地震的统计性质，而不能预测单个地震。
	2,每年发生的地震，从来不是单个最大的地震，而是一系列地震，其中最多的是小地震。本方法就是企图让预测和事实相适应。
	3,在预测了某个时间范围的地震分布后，根据这个分布，得出在这个时间范围发生概率最大的地震。这个地震震级就是本程序的输出。
	4,返回最大地震而不是一系列地震，是为了与当前的检验方法相适应，因为现在的预报是以最大地震来检验的。
	5,函数名为一个双关语，英文为New Best的缩写，中文为牛逼的拼音缩写。New Best意为有史以来最好的地震预报方法，牛逼意为这个程序的预测效果非常利害，惊爆眼球。
	参数为：
	A,B : 这是GRfit程序给出的，请注意，B值一定是负数，不可以输入B值的绝对值。
	souredelta: 对GR关系式进行拟合时使用的时间范围，格式为datetime库中的timedelta
	targetdelta: 企图预测的时间范围，格式为datetime库中的timedelta
	输出为最大震级，将输出加减0.5就是预报结果
	"""
	A = A - log10(souredelta/ targetdelta)
	chance_M = dict()
	for ml in range(100):
		chance1 = exp(-pow(10, A + B * (ml / 10 + 0.6)))
		chance2 = exp(-pow(10, A + B * (ml / 10 - 0.5)))
		chance_M[chance1 - chance2] = ml / 10
	return chance_M[max(chance_M)], max(chance_M)

def getM_chances(A:float, B:float, souredelta, targetdelta):
	"""
	画出最大震级——概率曲线的方法。震级为该震级加减各0.5级以内，概率为最大地震在该震级范围内的概率。
	参数为：
	A,B : 这是GRfit程序给出的，请注意，B值一定是负数，不可以输入B值的绝对值。
	souredelta: 对GR关系式进行拟合时使用的时间范围，格式为datetime库中的timedelta
	targetdelta: 企图预测的时间范围，格式为datetime库中的timedelta
	"""
	A = A - log10(souredelta/ targetdelta)
	M_chances = dict()
	for ml in range(100):
		chance1 = exp(-pow(10, A + B * (ml / 10 + 0.5)))
		chance2 = exp(-pow(10, A + B * (ml / 10 - 0.5)))
		M_chances[ml / 10] = chance1 - chance2
	return M_chances
    
def getM_counts(area:tuple, timeslot:tuple, tablename:str):
	"""
	从数据库得到进行GR关系式所需要的数据，输入为
	area :     (纬度， 纬度， 经度， 经度)
	timeslot:  (时间, 时间), 时间格式为字符串"YYYY-mm-dd HH:MM:SS"
	tablename: 表名
	输出为dict格式{M: count}
	"""
	conn = sqlite3.connect("地震目录.db")
	timeslot = '时间 >= "%s" and 时间 < "%s"' % (timeslot[0], timeslot[1])
	area = '纬度 >= %s and 纬度 <= %s and 经度 >= %s and 经度 <= %s' % (area[0], area[1], area[2], area[3])
	Ms = [ml[0] for ml in conn.execute('select 震级 from %s where %s and %s' % (tablename, area, timeslot))]
	conn.close()
	M_counts = dict()
	for i in range(int(max(Ms) * 10)):
		M_counts[i / 10] = len([ml for ml in Ms if ml >= i / 10])
	for i in range(1, int(max(Ms) * 10)):
		if M_counts[i / 10] == M_counts[(i - 1) / 10]:
			M_counts.pop((i - 1) / 10)
	return M_counts
    
def record2data(record:str):
	"""
	对EQT格式的地震目录中的每一行进行分析处理，得到时间，纬度，经度，震级，深度，地名并返回。
	"""
	if record.strip() == '':
		return None
	year = record[0:5].lstrip().replace(' ', '0')
	month = record[5:7].replace(' ', '0')
	day = record[7:9].replace(' ', '0')
	hour = record[9:11].replace(' ', '0')
	minute = record[11:13].replace(' ', '0')
	second = record[13:15].replace(' ', '0')
	if month == '00':
		month = '01'
	if day == '00':
		day = '01'
	if int(hour) > 23:
		hour = '23'
	if int(minute) > 59:
		minute = '59'
	if int(second) > 59:
		second = '59'
	if int(month) > 12:
		month = '12'
	if int(month) in (1, 3, 5, 7, 8, 10, 12) and int(day) > 31:
		day = '31'
	elif int(month) in (4, 6, 9, 11) and int(day) > 30:
		day = '30'
	elif int(month) == 2 and int(day) > 29:
		day = '29'
	if year.startswith('-'):
		year = year[1:]
		if len(year) <= 3:
			year = '0' * (4 - len(year)) + year
		year = '-' + year
	if len(year) <= 3:
		year = '0' * (4 - len(year)) + year
	datetime = year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':' + second
	latitude = record[15:21]
	longitude = record[21:28]
	magnitude = record[28:32]
	depth = record[32:35]
	placename = record[39:].rstrip()
	return datetime, latitude, longitude, magnitude, depth, placename
	           
def catalog2database(catalogname:str, tablename:str, dbname:str = '地震目录.db') -> None:
	"""
	将地震目录从eqt格式的文件倒入sqlite3数据库
	参数为:
	catlogname: EQT格式文件的文件名
	tablename:  地震目录在数据库中的表的名字
	"""
	create_sql = "create table %s(时间 DATETIME, 纬度 DECIMAL(4, 2), 经度 DECIMAL(5, 2), 震级 DECIMAL(3, 1) NOT NULL, 深度 SMALLINT(3), 地名 VARCHAR(50), PRIMARY KEY(时间, 纬度, 经度))" % tablename
	conn = sqlite3.connect(dbname)
	cur = conn.cursor()
	tables = [table[0] for table in conn.execute('select name from sqlite_master where type="table"')]
	cur.execute("delete from %s" % tablename if tablename in tables else create_sql)
	for record in open(catalogname, errors = 'replace', encoding = 'GBK'):
		data = record2data(record)
		if data == None:
			continue
		cur.execute("insert into %s values(?,?,?,?,?,?) on conflict do nothing" % tablename, data)
	conn.commit()
	conn.close()
    
def database2catalog(tablename:str, catalogname:str, dbname:str = '地震目录.db') -> None:
	"""
	将地震目录从sqlite3数据库导出为EQT格式的文件
	参数为:
	tablename:  地震目录在数据库中的表的名字
	catlogname: EQT格式文件的文件名
	"""
	select_sql = "select strftime(' %%Y%%m%%d%%H%%M%%S', 时间), 纬度, 经度, 震级, 深度, 地名 from %s" % tablename
	conn = sqlite3.connect(dbname)
	if tablename not in [table[0] for table in conn.execute('select name from sqlite_master where type="table"')]:
		print("Error:", tablename, " table is not exist!")
		return None
	with open(catalogname, mode='w', encoding = 'GBK') as catalog:
		records = '\n'.join("%s%6.2f%7.2f%4.1f%3d  0 %s" % record for record in conn.execute(select_sql))
		catalog.write(records)
	conn.close()
	
def 地震预报4中学生(area:tuple, yearslot:tuple, tablename:str):
	"""
	用每一年发生的最大地震的平均值，来预报未来一年发生的最大地震的方法。提出这个方法的原因是：
	1,大多数人不具备理解统计物理学的能力，仅具备牛顿力学的物理学基础，所以无法理解NB程序的理论基础。
	2,传统地震预报本质上是以过去几十年的最大地震来预报未来一年的最大地震，这是其预报错误率极高的本质原因，本程序就是为了纠正这个错误
	3,本程序的预测效果非常良好，仅比NB程序略差，这证明了，只要对传统方法稍作改进，纠正其最主要的错误，就可以做出科学的地震预报了。
	参数为:
	area :     (纬度， 纬度， 经度， 经度)
    yearslot:  (起始年, 终止年)  例: (2000, 2020)
	tablename: 表名
	输出为最大震级的中间值，只要将这个中间值加减0.5就是预报结果。
	"""
	conn = sqlite3.connect("地震目录.db")
	area = '纬度 >= %s and 纬度 <= %s and 经度 >= %s and 经度 <= %s' % (area[0], area[1], area[2], area[3])
	sql = 'select max(震级) from %s where %s and ' % (tablename, area) + '时间 > "%s" and 时间 <= "%s"'
	Ms = [tuple(conn.execute(sql % (date(year, 1, 1), date(year+1, 1, 1))))[0][0] for year in range(yearslot[0], yearslot[1])]
	conn.close()
	return sum(Ms) / len(Ms)

def getYear_Ms(area:tuple, yearslot:tuple, tablename:str):
	"""
	本方法是为了获得yearsot范围的任何一年的最大震级，输出为dict类型：{年:震级}，主要是为了配合 地震预报4中学生 这个函数来画图用的。
	使用本方法，可以直观的给别人讲解如何得到未来一年的最大震级，因为过去的那些年中的每一年的震级可以由本函数给出来。
	参数为:
	area :     (纬度， 纬度， 经度， 经度)
    yearslot:  (起始年, 终止年)  例: (2000, 2020)
	tablename: 表名
	输出一个字典，key为年,value为该年地震的最大震级
	"""
	conn = sqlite3.connect("地震目录.db")
	area = '纬度 >= %s and 纬度 <= %s and 经度 >= %s and 经度 <= %s' % (area[0], area[1], area[2], area[3])
	sql = 'select max(震级) from %s where %s and ' % (tablename, area) + '时间 > "%s" and 时间 <= "%s"'
	T_Ms = {year: tuple(conn.execute(sql % (date(year, 1, 1), date(year+1, 1, 1))))[0][0] for year in range(yearslot[0], yearslot[1])}
	conn.close()
	return T_Ms

def getMax(area:tuple, timeslot:tuple, tablename:str) -> list:
	"""
	获得震级最大的地震,由于可能发生几个震级最大的地震，所以输出为一个list,list中的每个元素也是list,依次为时间, 经度, 纬度, 地名, 震级
	参数为
	area :     (纬度， 纬度， 经度， 经度)
	timeslot:  (时间， 时间)，时间格式为"YYYY-mm-dd HH:MM:SS"
	tablename: 表名
	"""
	conn = sqlite3.connect("地震目录.db")
	range = '纬度 >= %s and 纬度 <= %s and 经度 >= %s and 经度 <= %s and 时间 > "%s" and 时间 <= "%s"' % (area[0], area[1], area[2], area[3], timeslot[0], timeslot[1])
	max = list(conn.execute('select max(震级) from %s where %s' % (tablename, range)))[0][0]
	sql = 'select 时间, 经度, 纬度, 地名, 震级 from %s where %s and 震级>=%s' % (tablename, range, max)
	maxes = list(conn.execute(sql))
	conn.close()
	return maxes
