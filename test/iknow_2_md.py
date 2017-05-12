# encoding: utf8
import requests	
from bs4 import BeautifulSoup
import time
import re
import sqlite3

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

#获取当前时间
def getCurrentTime():
	return time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))

class IKNOWTOMARKDOWN:
	'''读取百度知道指定用户回答内容，存储为Markdown文件'''


	def __init__(self):
		# 连接信息
		self.base_url = "https://www.baidu.com/p/sys/data/zhidao/anslist"
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.5 Safari/537.36',
			'Referer':    'https://www.baidu.com/p/skycolorwater?from=tieba'
		}
		self.page_increment = 1 # 每页增量

		self.qlist = []  # 当前页需要处理记录列表
		self.failed_qlist = [] # 失败记录
		self.total = 0

		self.errorlog = open('log.log', 'a')
		self.errorlog.write('%s\n' % getCurrentTime())


	def __getPage(self):
		'''获取当前页数据'''

		# 提交参数
		param = {
			'portrait': self.uid,
			'pn'      : self.this_page,
			'rec'     : 3000005,
			't'       : "%d" % (time.time()*1000)
		}
		try:
			response = requests.get(self.base_url, params=param, headers=self.headers)
		except Exception:
			msg = "[error] 读取第%d页失败" % self.this_page
			raise Exception(msg)		

		res = response.text.replace(r'x22','"').replace('\\','')
		# res = re.search(re.compile(r'"tplContent":"(.*?)',re.S), res).group()
		res = re.search(re.compile(r'(?<="tplContent":)(.*?)(?=$)',re.S), res).group()

		soup = BeautifulSoup(res, "lxml")

		self.content = soup.find('table', class_='zhidao-anwlist-body')

		return

	def __nextPage(self):
		'''试图获取当前页数据'''		

		print
		print getCurrentTime(), u" 开始读取第%d页数据..." % self.this_page

		n = 0
		# 由于可能间歇性获取不到数据，所以允许原地请求5次
		while True:
			self.__getPage()
			n += 1
			if self.content or n==5:
				break

		if self.content:
			self.this_page += self.page_increment
		else:
			msg = "[error] 读取第%d页失败" % self.this_page
			raise Exception(msg)

		return	

	def __getList(self):
		'''获取回答列表'''

		self.__nextPage()
		items = self.content.find_all("tr", class_="anwlist-item") # 每一行记录
		for tr in items:

			# 标题及编号
			title = tr.find('a')    # 标题元素
			href = title['href'].split('\?')[0] # 问题url
			aid = (re.findall("\d+", href))[0]

			# 日期	
			date = tr.find('td', class_='zhidao-item-date') # 日期单元格

			li = (aid, title.string.strip(), date.string.strip())
			self.qlist.append(li)

		return

	def __log(self, msg):
		'''错误日志'''

		print msg
		self.errorlog.write("%s\n" % msg);

		return

	def __save_file(self, filename, url):
		'''根据链接下载文件'''

		failed = 0
		max_failed = 5

		obj = requests.get(url)

		while obj.status_code != 200 :

			if failed == max_failed:
				break
			else:
				obj = requests.get(url)
				failed +=1

			
		if failed < max_failed:
			with open(filename, 'wb') as f:
				f.write(obj.content)
			return True
		else:
			return False



	def __generate(self, item):
		'''根据当前回答记录生成markdown文件'''

		print getCurrentTime(), u" 当前问题编号：%s" % item[0]

		# 搜集数据
		url = 'https://zhidao.baidu.com/question/%s.html' % item[0]
		response = requests.get(url, headers=self.headers)
		response.encoding = 'gbk'
		soup = BeautifulSoup(response.text, "lxml")

		# 1 提问内容
		tag = soup.find("div", id="wgt-ask") # 定位提问
		content_obj = tag.find("span", class_='con')
		q_content = []
		if content_obj:
			q_content = ["%s\n\n" % string for string in content_obj.stripped_strings]

		q_imgs = tag.find_all('li', class_='q-img-li')
		q_img_list = []

		if len(q_imgs)==1:
			img_name = 'q-%s.jpg' % item[0]
			q_img_list.append(img_name)
			if not self.__save_file('_images/' + img_name, q_imgs[0]['data-src']):
				msg = "[error]: failed to download image: %s" % item[0]
				raise Exception(msg)

		elif len(q_imgs)>1:
			i = 0
			for img in q_imgs:
				i += 1
				img_name = 'q-%s-%d.jpg' % (item[0], i)
				q_img_list.append(img_name)
				if not self.__save_file('_images/' + img_name, img['data-src']):
					msg = "[error]: failed to download image: %s" % item[0]
					raise Exception(msg)
		q_img_content = ['<div align=\'center\'><img src="{{ \'%s\' | prepend: site.uploads | prepend: site.baseurl }}"></div>\n\n' % img for img in q_img_list]


		# 2 回答内容

		# 先找到回答者，然后追溯到回答内容
		a_tag = soup.find("a", class_="user-name", text="\n%s\n" %self.username) # 定位回答者
		a_tag = a_tag.find_parent("div", class_="line")
		obj = a_tag.find_previous_sibling("div", id=True)
		if not obj.attrs.has_key('accuse'):
			obj = obj.find(attrs={'accuse':True})
		a_content = [] # 文本
		a_content += ["%s\n\n" % string for string in obj.stripped_strings] # 文本


		# 图片
		a_imgs = obj.find_all('a', href=True) # 图片链接放在a标签中
		a_img_list = []

		if len(a_imgs)==1:
			img_name = 'a-%s.jpg' % item[0]
			a_img_list.append(img_name)
			if not self.__save_file('_images/' + img_name, a_imgs[0]['href']):
				msg = "[error]: failed to download image: %s" % item[0]
				raise Exception(msg)

		elif len(a_imgs)>1:
			i = 0
			for img in a_imgs:
				i += 1
				img_name = 'a-%s-%d.jpg' % (item[0], i)
				a_img_list.append(img_name)
				if not self.__save_file('_images/' + img_name, img['href']):
					msg = "[error]: failed to download image: %s" % item[0]
					raise Exception(msg)

		a_img_content = ['<div align=\'center\'><img src="{{ \'%s\' | prepend: site.uploads | prepend: site.baseurl }}"></div>\n' % img for img in a_img_list]


		# 保存数据
		filename = '_posts/%s-%s.md' %(item[2], item[0])
		with open(filename, 'w') as f:

			# title

			title = '''---
			layout: post
			author: %s
			title : %s
			tags  : 
			---
			''' % (self.username, item[1])
			f.write("%s\n\n" % title.replace("\t","").strip())

			# question
			f.writelines(q_content)
			f.writelines(q_img_content + ['\n\n', '---', '\n\n'])

			# answer
			f.writelines(a_content)
			f.writelines(a_img_content)

		self.total += 1

		return


	def run(self, username, uid, startPage=1, numPage=1, maxFail=5):
		# 初始化参数
		self.this_page = startPage # 当前页
		self.content = None # 当前页面数据
		self.username = username
		self.uid = uid

		max_page = startPage+numPage

		total = 0 # 总记录数

		print u"统计[%s]的回答记录..." % username
		print "----------------------------------------------------------"

		fail = 0

		# 循环插入数据
		while True:	

			# 达到失败次数就停止
			if fail > maxFail:
				break

			time.sleep(1)

			# 列表有数据则处理，没数据则获取之
			if len(self.qlist):
				item = self.qlist.pop()
				# self.__generate(item)
				try:
					self.__generate(item)
				except Exception as msg:
					self.__log(u"%s: %s" %(item[0], msg))
					self.failed_qlist.append(item)
					continue

			else:

				# 达到要求的页数就终止
				if numPage and self.this_page == max_page:
					break

				# 请求数据
				try:
					self.__getList()
				except Exception as msg:
					self.__log(u"%s" %(msg))
					self.failed_qlist.append(item)
					continue

				# 如果请求后还没有数据，那就算失败一次
				if not len(self.qlist):
					fail += 1
		
		# 查缺补漏
		fail = 0
		while len(self.failed_qlist):

			if fail == 0:
				print '\n', getCurrentTime(), u" 读取完毕，开始查缺补漏："
			elif fail == 5:
				break

			item = self.failed_qlist.pop()

			try:
				self.__generate(item)
			except Exception as msg:
				self.__log(u"%s: %s" %(item[0], msg))
				self.failed_qlist.append(item)
				fail += 1
				continue

		print
		print getCurrentTime(), u" 当前第%s页" % (self.this_page-1)
		print getCurrentTime(), u" 共搜集记录数：%s" % self.total

		self.errorlog.write(u"End: 当前第%d页\n" % (self.this_page-1))
		self.errorlog.close()
		return


if __name__ == '__main__':

	username = 'learneroner'
	uid = '79fe4069236f25705e79e406'

	I = IKNOWTOMARKDOWN()
	I.run(username,uid,1,2)