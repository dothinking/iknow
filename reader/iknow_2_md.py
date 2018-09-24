# encoding: utf8
# python 3.6

import requests
from bs4 import BeautifulSoup
import time
import re
import html

class IKNOWTOMARKDOWN:
	'''读取百度知道指定用户回答内容，存储为Markdown文件'''
	def __init__(self):
		# 连接信息
		self.url_list = "https://zhidao.baidu.com/mucenter/ajax/getAnswer"
		self.url_ques = 'https://zhidao.baidu.com/question/'
		self.url_anws = 'http://zhidao.baidu.com/msearch/ajax/getsearchqb'
		self.url_query = 'https://zhidao.baidu.com/msearch/ajax/getsearchlist' # {word: xx, pn: xx}

		# mobile
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
			'Connection': 'keep-alive',
			'Accept-Encoding': 'gzip, deflate, sdch, br',
			'Host': 'zhidao.baidu.com',
			'Referer': 'https://zhidao.baidu.com/'
		}

		self.page_increment = 20 # 每页记录数
		self.more_page = True    # 是否还有下一页数据

		self.qlist = []        # 当前页需要处理记录列表
		self.failed_qlist = [] # 失败记录
		self.total = 0         # 成功获取到的记录数

		# 日志
		self.log = open('log.log', 'a', encoding='utf-8')
		self.__log("开启记录")

		# 本地存储图片的全路径
		self.img_url_pattern = '<div align=\'center\'><img src="{{ \'{0}\' | prepend: site.uploads | prepend: site.baseurl }}"></div>\n\n'

		return

	def run(self, username, startPage=1, numPage=1, maxFail=5):
		'''主进程'''
		# 初始化参数
		self.this_page = startPage # 当前页
		self.username  = username
		max_page = startPage+numPage

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
					self.__log("ERROR: {0}".format(msg))
					self.failed_qlist.append(item)

			else:

				# 达到要求的页数就终止
				if self.this_page == max_page: break

				# 超出总页数也得停止
				if not self.more_page: break

				# 请求数据
				try:
					self.fetch_list()
				except Exception as msg:
					self.__log("ERROR: {0}".format(msg))

				# 如果请求后还没有数据，那就算失败一次
				if not len(self.qlist):
					fail += 1
		
		# 查缺补漏
		if len(self.failed_qlist):
			self.__log()
			self.__log("读取完毕，开始查缺补漏：")

		fail = 0
		while len(self.failed_qlist):
			if fail == maxFail: break
			item = self.failed_qlist.pop()
			try:
				self.fetch_content(item)
			except Exception as msg:
				self.__log("ERROR: {0}".format(msg))
				self.failed_qlist.append(item)
				fail += 1
				continue
		
		# 结束
		self.__log()
		res = "当前第{0}页，共搜集记录数：{1}".format(self.this_page - 1, self.total)
		self.__log(res)
		self.__log("记录完毕")
		self.__log()
		self.log.close()
		return

	def fetch_list(self):
		'''获取当前页问题列表'''

		self.__log()
		self.__log("读取第%d页数据..." % self.this_page)

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
			raise Exception("读取第{0}页失败".format(self.this_page))

		# 记录总数及当前页数据
		data =  response['data']['list']['entry']
		self.more_page = response['data']['list']['hasMore']

		for item in data:
			li = (item['qid'], html.unescape(item['title']), item['reply_create_time'])
			self.qlist.append(li)

		# 检测解析数据是否成功
		assert len(self.qlist), "解析第%d页失败" % self.this_page

		self.this_page += 1
		return

	def fetch_content(self, item):
		'''获取问题内容'''

		self.__log("当前问题编号：%s" % item[0])

		# 搜集数据
		url = self.url_ques + item[0]
		response = requests.get(url, headers=self.headers)
		response.encoding = 'utf-8'
		soup = BeautifulSoup(response.text, "html.parser")

		# 问题内容
		q_content, q_img_content = self.__fetch_question(soup, item[0])

		# 回答内容
		a_content, a_img_content = self.__fetch_answer(soup, item[0])		

		# 3 保存数据
		filename = '_posts/{0}-{1}.md'.format(item[2], item[0])
		with open(filename, 'w', encoding='utf-8') as f:
			# title
			title = '''---
			layout: post
			author: {0}
			title : {1}
			tags  : 不定积分
			---\n\n
			'''.format(self.username, item[1]).replace("\t","")
			f.write(title)

			# question
			f.writelines(q_content)
			f.writelines(q_img_content)

			# seperate
			f.writelines(['\n\n', '---', '\n\n'])

			# answer
			f.write(a_content)
			f.writelines(a_img_content)

		self.total += 1

		return

	def __log(self, msg=''):
		'''日志'''
		if msg:
			now = time.strftime('[%Y-%m-%d %H:%M:%S]',time.localtime(time.time()))
			msg = "%s %s" % (now, msg)

		# print(msg)
		self.log.write(msg+'\n')
		self.log.flush()
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

	def __fetch_question(self, dom, qid):
		'''获取提问内容'''

		# 检测能否访问此问题
		obj = dom.find(class_='wgt-question')		
		assert obj, "问题已失效"

		# 提问文本
		obj_content = obj.find(class_='wgt-question-desc-inner')
		q_content = ["{0}\n\n".format(line) for line in obj_content.stripped_strings] if obj_content else []

		# 提问图片
		q_imgs = []
		for i, obj_img in enumerate(obj.find_all(class_='wgt-question-image-item'), start=1):
			img_name = 'q-{0}.jpg'.format(qid) if i==1 else 'q-{0}-{1}.jpg'.format(qid, i)
			if self.__save_file('_images/' + img_name, obj_img['data-src']):
				q_imgs.append(img_name)
			else:
				raise Exception("下载第{0}幅提问图片失败".format(i))		
		q_img_content = [self.img_url_pattern.format(img) for img in q_imgs]

		return q_content, q_img_content

	def __fetch_answer(self, dom, qid):
		'''获取回答内容：提取回答的rid后用api获取json数据'''

		# 定位回答者
		author = dom.find("a", text=re.compile("%s" % self.username))
		if not author: # 回答被折叠
			script_reply = dom.find('script', id='reply-wgt-tmpl')
			if script_reply:
				hidden_dom = BeautifulSoup(script_reply.text, "html.parser")
				author = hidden_dom.find("a", text=re.compile("%s" % self.username))

		assert author, "暂未发现回答者"

		# 获取回答id
		reply_item = author.find_parent("div", class_="question-author-container").find_next_sibling("div")		
		prefix = 'reply-item-'
		for class_name in reply_item.attrs['class']:
			if prefix in class_name:
				rid = class_name.replace(prefix, '')
				break
		else:
			raise Exception('未找到回答记录')

		# 从api接口获取json数据
		param = {
			'qid': qid,
			'rid': rid
		}
		try:
			response = requests.get(self.url_anws, params=param, headers=self.headers).json()
		except Exception:
			raise Exception("获取回答内容失败")

		assert response.get('errno', 1)==0, '获取回答内容失败'

		# 文本
		a_content = response['data']['content'].replace("<br />", "\n\n")
		a_content = html.unescape(a_content) # HTML解码：'&gt;' => '>'

		# 图片
		img_urls = [url[0] for url in response['data']['imgUrl']] if response['data']['imgUrl'] else []
		a_imgs = []
		for i, url in enumerate(img_urls, start=1):
			img_name = 'a-{0}.jpg'.format(qid) if i==1 else 'a-{0}-{1}.jpg'.format(qid, i)
			if self.__save_file('_images/' + img_name, url):
				a_imgs.append(img_name)
			else:
				raise Exception("下载第{0}幅回答图片失败".format(i))

		a_img_content = [self.img_url_pattern.format(img) for img in a_imgs]

		return a_content, a_img_content		

if __name__ == '__main__':

	username = 'learneroner'

	I = IKNOWTOMARKDOWN()

	I.run(username,141,5)


	