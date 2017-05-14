# encoding: utf8
import requests, urllib, HTMLParser
from bs4 import BeautifulSoup
import time, sys, re

reload(sys)
sys.setdefaultencoding( "utf-8" )

class IKNOWTOMARKDOWN:
	'''读取百度知道指定用户回答内容，存储为Markdown文件'''


	def __init__(self):
		# 连接信息
		self.url_list = "https://zhidao.baidu.com/mucenter/ajax/getAnswer"
		self.url_ques = 'https://zhidao.baidu.com/question/'
		self.url_anws = 'http://zhidao.baidu.com/msearch/ajax/getsearchqb'

		# mobile
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, sdch, br',
			'Host': 'zhidao.baidu.com'
		}

		self.max_page = 100      # 初始化最大页面数
		self.page_increment = 20 # 每页记录数

		self.qlist = []        # 当前页需要处理记录列表
		self.failed_qlist = [] # 失败记录
		self.total = 0         # 成功获取到的记录数

		# 日志
		self.log = open('log.log', 'a')
		self.log.write(u"开启记录")

		return

	def fetch_list(self):
		'''获取当前页问题列表'''

		self.__log(u" 读取第%d页数据..." % self.this_page)

		# 提交参数
		param = {
			'un': self.username,
			'pn': (self.this_page-1) * self.page_increment,
			'rn': self.page_increment
		}

		# 从api接口获取json数据
		try:
			response = requests.get(self.url_list, params=param).json()
		except Exception:
			msg = "读取第%d页失败" % self.this_page
			raise Exception(msg)

		# 记录总数及当前页数据
		data =  response['data']['list']['entry']
		total = response['data']['list']['total']

		self.max_page = int(total/self.page_increment) + 1

		for item in data:
			li = (item['qid'], item['title'], item['reply_create_time'])
			self.qlist.append(li)

		# 检测解析数据是否成功
		if len(self.qlist):
			self.this_page += 1
		else:
			msg = "解析第%d页失败" % self.this_page
			raise Exception(msg)

		return


	def __log(self, msg='\n'):
		'''日志'''
		if msg != '\n':
			now = time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))
			msg = "%s %s\n" % (now, msg)

		print msg
		self.log.write(msg)

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

	def fetch_content(self, item):
		'''获取问题内容'''

		self.__log(u" 当前问题编号：%s" % item[0])

		# 搜集数据
		url = self.url_ques + item[0]
		response = requests.get(url, headers=self.headers)
		response.encoding = 'utf-8'

		soup = BeautifulSoup(response.text, "html.parser")

		# 检测能否访问此问题
		try:
			obj = soup.find(class_='w-question-box')
		except Exception:
			msg = "问题已失效" % self.this_page
			raise Exception(msg)


		# 1 提问文本
		q_content = []
		if obj.find(class_='cont'):
			q_content = ["%s\n\n" % string for string in obj.find(class_='cont').stripped_strings]

		# 提问图片
		q_imgs = []
		obj_imgs = obj.find_all(class_='q-img')
		i = 0
		for obj_img in obj_imgs:

			i += 1

			# url 解码
			url = obj_img['data-bigurl'].split('src=')[1]
			img_url = urllib.unquote(url)

			# 下载
			if i==1:
				img_name = 'q-%s.jpg' % item[0]
			else:
				img_name = 'q-%s-%d.jpg' % (item[0], i)

			if self.__save_file('_images/' + img_name, img_url):
				q_imgs.append(img_name)
			else:
				msg = "下载第%d幅提问图片失败" % i
				raise Exception(msg)

		q_img_content = ['<div align=\'center\'><img src="{{ \'%s\' | prepend: site.uploads | prepend: site.baseurl }}"></div>\n\n' % img for img in q_imgs]

		# 2 回答内容：可以直接提取内容，这里提取回答的rid，然后直接调用api获取json数据

		# 先找到回答者，然后追溯到回答内容
		# 注意高质量回答和普通回答渲染形式的不同
		a_tag = soup.find("span", class_="name", text=re.compile("%s" %self.username))
		if a_tag:
			tag = a_tag.find_parent("div", class_="replier-info")
		else:
			a_tag = soup.find("a", class_="ask-name-mavin", text="%s" %self.username)
			tag = a_tag.find_parent("div", class_="quality-info")

		# 获取回答id
		obj = tag.find_next_sibling("div").find('div', attrs={'data-rid': True})
		rid = obj['data-rid']

		# 从api接口获取json数据
		param = {
			'qid': item[0],
			'rid': rid
		}
		try:
			response = requests.get(self.url_anws, params=param).json()
		except Exception:
			msg = "读取回答内容失败"
			raise Exception(msg)

		# 文本
		a_content = response['data']['content'].replace("<br />", "\n\n")
		a_content = HTMLParser.HTMLParser().unescape(a_content) # HTML解码：'&gt;' => '>'

		# 图片
		img_urls = []
		if response['data']['imgUrl']:
			img_urls = [url[0] for url in response['data']['imgUrl']]

		i = 0
		a_imgs = []
		for url in img_urls:

			i += 1

			# 下载
			if i==1:
				img_name = 'a-%s.jpg' % item[0]
			else:
				img_name = 'a-%s-%d.jpg' % (item[0], i)

			if self.__save_file('_images/' + img_name, url):
				a_imgs.append(img_name)
			else:
				msg = "下载第%d幅回答图片失败" % i
				raise Exception(msg)

		a_img_content = ['<div align=\'center\'><img src="{{ \'%s\' | prepend: site.uploads | prepend: site.baseurl }}"></div>\n\n' % img for img in a_imgs]


		# 3 保存数据
		filename = '_posts/%s-%s.md' %(item[2], item[0])
		with open(filename, 'w') as f:

			# title
			title = '''---
			layout: post
			author: %s
			title : %s
			tags  : 不定积分
			---
			''' % (self.username, item[1])
			f.write("%s\n\n" % title.replace("\t","").strip())

			# question
			f.writelines(q_content)
			f.writelines(q_img_content + ['\n\n', '---', '\n\n'])

			# answer
			f.write(a_content)
			f.writelines(a_img_content)

		self.total += 1

		return


	def run(self, username, startPage=1, numPage=1, maxFail=5):
		'''主进程'''
		# 初始化参数
		self.this_page = startPage # 当前页
		self.username  = username
		max_page = startPage+numPage

		print u"统计[%s]的回答记录..." % username
		print "----------------------------------------------------------"

		fail = 0

		# 循环插入数据
		while True:	

			# 达到失败次数就停止
			if fail == maxFail:
				break

			# 列表有数据则处理，没数据则获取之
			if len(self.qlist):
				item = self.qlist.pop()
				try:
					self.fetch_content(item)
					time.sleep(1)
				except Exception as msg:
					self.__log(u"ERROR: %s" % msg)
					self.failed_qlist.append(item)

			else:

				# 达到要求的页数就终止
				if numPage and self.this_page == max_page:
					break

				# 超出总页数也得停止
				if self.this_page > self.max_page:
					break

				# 请求数据
				try:
					self.fetch_list()
				except Exception as msg:
					self.__log(u"ERROR: %s" % msg)

				# 如果请求后还没有数据，那就算失败一次
				if not len(self.qlist):
					fail += 1
		
		# 查缺补漏
		if len(self.failed_qlist):
			self.__log()
			self.__log(u" 读取完毕，开始查缺补漏：")

		fail = 0
		while len(self.failed_qlist):

			if fail == maxFail: break

			item = self.failed_qlist.pop()

			try:
				self.fetch_content(item)
			except Exception as msg:
				self.__log(u"ERROR: %s" % msg)
				self.failed_qlist.append(item)
				fail += 1
				continue
		# 结束
		self.down()
		return

	def down(self):
		'''清理数据'''
		# 小结
		self.__log()
		res = u" 当前第%d页，共搜集记录数：%s\n" % (self.this_page - 1, self.total)
		self.__log(res)
		self.__log(u"记录完毕")
		self.log.close()
		return


if __name__ == '__main__':

	username = 'learneroner'

	I = IKNOWTOMARKDOWN()

	I.run(username,3)