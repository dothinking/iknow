# encoding: utf8
import requests	
from bs4 import BeautifulSoup
import time
import sqlite3

#获取当前时间
def getCurrentTime():
	return time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))

class PoetryReader:
	'''读取古诗文网《唐诗三百首》，存入sqlite'''
	def __init__(self):
		# 连接信息
		self.base_url = "http://www.gushiwen.org/gushi/tangshi.aspx"
		self.page_url = "http://www.gushiwen.org"
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.5 Safari/537.36',
			'Referer'   : self.base_url
		}

		# 数据库
		self.dbName = 'poetry'

	def __getPoetry(self):
		'''获取给定url页面的诗词'''
		response = requests.get(self.base_url, headers=self.headers)
		soup = BeautifulSoup(response.text, "lxml")
		poetry_area = soup.find_all('div', class_='son2s')
		poetry = poetry_area[1].find_all('a')
		content = []
		for item in poetry:
			txt = item.string.split('(')
			if len(txt) == 2:
				content.append([item['href'], txt[0], txt[1][:-1]])
		return content

	def __getPoetryContent(self, url):
		'''获取给定url页面的诗词'''
		response = requests.get(url, headers=self.headers)
		soup = BeautifulSoup(response.text, "lxml")
		poetry_area = soup.find('div', class_='authorShow')
		content = poetry_area.find('p').text
		return content

	def read(self):
		# 初始化参数
		con = sqlite3.connect(self.dbName + '.db')

		print u"开始抓取《唐诗三百首》"
		print "----------------------------------------------------------"

		# 新建数据表
		con.execute('DROP TABLE IF EXISTS ' + self.dbName)
		con.execute('''CREATE TABLE %s (
			TITLE          CHAR    NOT NULL,
			AUTHOR         CHAR    NOT NULL,
			CONTENT        TEXT    NOT NULL);''' % self.dbName)

		print getCurrentTime(), u" 创建数据表"

		# 循环插入数据
		poetry = self.__getPoetry()
		lists = []
		num = 1
		for item in poetry:
			print getCurrentTime(), u" 当前记录 %d：" % num + item[1] + " | " + item[2]
			content = self.__getPoetryContent(self.page_url + item[0])
			li = (item[1], item[2], content)
			lists.append(li)
			num += 1

		# 批量插入数据库
		try:
			con.executemany('INSERT INTO ' + self.dbName + ' VALUES (?,?,?)', lists)
			con.commit()
		except sqlite3.Error as e:
			print "An error occurred:", e.args[0]
			return
		
		# 输出
		cur = con.cursor()
		cur.execute("SELECT COUNT(TITLE) FROM " + self.dbName)
		num =  cur.fetchone()[0]
		print "----------------------------------------------------------"
		print u"总计: %d 首" % num

		# 提交数据，关闭连接
		if not num:
			con.execute('DROP TABLE '+self.dbName)

		con.commit()
		con.close()

		return

if __name__ == '__main__':
	I = PoetryReader()
	I.read()