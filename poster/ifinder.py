# encoding: utf8
import requests	
from bs4 import BeautifulSoup
import random


class IFinder:
	'''question lists'''
	def __init__(self):
		self.title = '[FINDER] '
		print self.title, 'init question finder...'
		# connection
		self.base_url = "https://zhidao.baidu.com/list"
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.5 Safari/537.36',
			'Referer':    'https://zhidao.baidu.com/list'
		}

		# control parameters
		self.questions = []
		self.num_per_page = 50
		self.current_page = 3
		self.question_lower_rate = 1/5.0
		self.question_upper_rate = 1/3.0

		return

	def __questions_list(self, tag):
		'''		
		:param tag: 
		:param page: 
		:return: 
		'''
		# post data
		self.current_page += 1
		param = {
			'tag' : tag,
			'ie'      : 'utf8',
			'rn'      : self.num_per_page,
			'pn'      : (self.current_page - 1) * self.num_per_page
		}

		# get page
		response = requests.get(self.base_url, params=param, headers=self.headers)
		response.encoding = 'gbk'
		soup = BeautifulSoup(response.text, "lxml")

		# question no lists
		# <li class ="question-list-item" data-qid="652213446813538285" data-cid="1078">...</li>
		# <li class ="question-list-item" data-qid="1835930462926489700" data-cid="89">... </li>
		items = soup.find_all("a", class_="title-link")
		ques = [ (li['href'], li.string.replace("\n", "")[0:30]) for li in items]

		if not ques:
			raise Exception('can not get more questions')

		# filter questions randomly
		num = len(ques)
		questions = random.sample(ques, random.randint(int(self.question_lower_rate*num), int(self.question_upper_rate*num)))
		self.questions = questions

		return

	def get_question(self, tag=u'百度'):
		'''
		pop question
		:param tag: 
		:return: 
		'''
		if not self.questions:
			self.__questions_list(tag=tag)

		# url for current question
		this_question = self.questions.pop()
		print self.title, 'question url   : %s' % this_question[0]
		print self.title, 'question title : %s' % this_question[1]

		return this_question

if __name__ == '__main__':

	I = IFinder()
	I.get_question()
