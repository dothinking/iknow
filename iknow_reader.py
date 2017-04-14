# encoding: utf8
import requests	
from bs4 import BeautifulSoup
import time
import re
import sqlite3

#获取当前时间
def getCurrentTime():
	return time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))

class IKNOWREADER:
	'''读取百度知道用户回答列表，存入数据库'''
	def __init__(self):
		# 连接信息
		self.base_url = "https://www.baidu.com/p/sys/data/zhidao/anslist"
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.5 Safari/537.36',
			'Referer':    'https://www.baidu.com/p/skycolorwater?from=tieba'
		}
		self.page_increment = 1 # 每页增量		

		# 数据库
		self.dbName = 'iknow.db'

	def __getPage(self):
		'''获取当前页数据'''

		# 提交参数
		param = {
			'portrait': self.uid,
			'pn'      : self.this_page,
			'rec'     : 3000005,
			't'       : "%d" % (time.time()*1000)
		}
		response = requests.get(self.base_url, params=param, headers=self.headers)

		res = response.text.replace(r'x22','"').replace('\\','')
		# res = re.search(re.compile(r'"tplContent":"(.*?)',re.S), res).group()
		res = re.search(re.compile(r'(?<="tplContent":)(.*?)(?=$)',re.S), res).group()

		soup = BeautifulSoup(res, "lxml")

		self.content = soup.find('table', class_='zhidao-anwlist-body')

		return

	def __nextPage(self):
		'''试图获取当前页数据'''

		self.this_page += self.page_increment

		n = 0
		# 由于可能间歇性获取不到数据，所以允许原地请求5次
		while True:
			self.__getPage()
			n += 1
			if self.content or n==5:
				break

		if self.content:
			print getCurrentTime(), u" 读取第%d页数据..." % self.this_page
		else:
			print getCurrentTime(), u" 无法读取第%d页数据..." % self.this_page

		return	

	def __getList(self,con):
		'''获取回答列表'''
		alists = []

		items = self.content.find_all("tr", class_="anwlist-item") # 每一行记录
		for tr in items:

			# 标题及编号
			title = tr.find('a')    # 标题元素
			href = title['href'].split('\?')[0] # 问题url
			aid = (re.findall("\d+", href))[0]

			# 是否采纳			
			if tr.find('span', class_='zhidao-adpt'):   # 采纳
				adopt = 1
			else:
				adopt = 0

			# 赞同数
			good = tr.find('span',class_='zhidao-good-item')
			if good:
				num = int(good.string) # 点赞数
			else:
				num = 0

			# 日期	
			date = tr.find('td', class_='zhidao-item-date') # 日期单元格

			li = (aid, title.string, adopt, num, date.string)
			alists.append(li)

		# 批量插入数据库
		try:
			con.executemany('INSERT INTO '+self.username+' VALUES (?,?,?,?,?)', alists)
			con.commit()
		except sqlite3.Error as e:
			print "An error occurred:", e.args[0]
			return

		print getCurrentTime(), u" 插入%d条记录..." % len(alists)

		return

	def read(self, username, uid, maxPages=0):
		# 初始化参数
		self.this_page = 0 # 当前页
		self.content = None # 当前页面数据
		self.username = username
		self.uid = uid
		self.total = 0 # 总记录数

		con = sqlite3.connect(self.dbName)

		print u"统计[%s]的回答记录..." % username
		print "----------------------------------------------------------"

		# 新建数据表
		con.execute('DROP TABLE IF EXISTS '+self.username)
		con.execute('''CREATE TABLE %s
			(AID INT PRIMARY KEY   NOT NULL,
			TITLE          TEXT    NOT NULL,
			ADOPTED        INT     NOT NULL,
			GOOD           INT     NOT NULL,
			ADATE          CHAR    NOT NULL);''' % self.username)

		print getCurrentTime(), u" 创建数据表"

		# 循环插入数据
		while True:
			# 达到要求的页数就终止
			if maxPages and self.this_page == maxPages:
				break
			# 获取下一页
			self.__nextPage()
			if not self.content: # 没有数据了就终止 / 暂未考虑其他原因导致获取不到数据的情况
				break
			# 读取数据
			self.__getList(con)			
		
		# 输出
		cur = con.cursor()
		cur.execute("SELECT COUNT(aid) FROM " + self.username)
		num =  cur.fetchone()[0]
		print "----------------------------------------------------------"
		print u"总计: %d 条" % num

		# 提交数据，关闭连接
		if not num:
			con.execute('DROP TABLE '+self.username)

		con.commit()
		con.close()

		return

I = IKNOWREADER()
# I.read("skycolorwater","f31e4069236f25705e79bb68")