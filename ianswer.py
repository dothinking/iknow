# encoding=utf8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time, pickle


class IAnswer:

	def __init__(self, cookie='', browser=0):
		'''
		init driver
		:param cookie: pickle name for cookie
		:param browser: 1 chrome, others phantomjs
		'''
		self.title = '[ANSWER] '
		print self.title, 'init answer driver...'
		self.cookie = cookie

		# login url
		self.login_url = "https://passport.baidu.com/v2/?login"
		self.cookie_login_url = "https://www.baidu.com"

		# header
		headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
			'Connection': 'keep-alive',
		}
		for key, value in headers.iteritems():
			DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

		# setting
		settings = {
			'userAgent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
			'loadImages': False
		}
		for key, value in settings.iteritems():
			DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.{}'.format(key)] = value

		# service_args
		service_args = [
			# '--load-images=false'
			# '--proxy=127.0.0.1:9999',
			#  '--proxy-type=http',
			#  '--ignore-ssl-errors=true'
		]

		# browser: 1 chrome, 2 firefox, others phantomjs
		if browser == 1 :
			self.driver = webdriver.Chrome()
		else:
			self.driver = webdriver.PhantomJS(service_args=service_args)

		# set browser size
		# to fix bug 'Element is not currently visible and may not be manipulated'
		self.driver.maximize_window()

		# waiting time
		self.wait = WebDriverWait(self.driver, 5)
		self.short = 3
		self.long = 10

		# login
		self.__login()
		return

	def __login(self):
		'''
		login
		'''
		# if cookie is null, login by username
		if(self.cookie):
			self.__login_by_cookie()
		else:
			self.__login_by_username()

		# finally, login success
		print self.title, 'login success, welcome ' + self.username
		# print cookies
		# print self.driver.get_cookies()
		time.sleep(self.short) # attention! waiting for redirection and complete login

		return

	def __login_by_username(self):
		'''
		login by username
		'''
		print self.title, 'login by username...'
		# load login page
		self.driver.get(self.login_url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_id('TANGRAM__PSP_3__submit').is_displayed())
		except:
			raise Exception('load login page failed.')

		username = raw_input('[INPUT ] enter username:\n')
		password = raw_input('[INPUT ] enter password:\n')

		# fill form and submit
		self.username = username
		username_input = self.driver.find_element_by_id('TANGRAM__PSP_3__userName')  # email
		username_input.clear()
		for c in username: # avoid incomplete input
			username_input.send_keys(c)

		pswd_input = self.driver.find_element_by_id('TANGRAM__PSP_3__password')  # password
		pswd_input.clear()
		for c in password:
			pswd_input.send_keys(c)

		self.driver.find_element_by_id('TANGRAM__PSP_3__submit').click()  # submit

		# check login status
		# success: current url changes to be redirect url, otherwise failed
		try:
			self.wait.until(lambda the_driver: the_driver.current_url != self.login_url)
		except:
			# login failed, check verify code
			# considering mistaking input, while loop is used
			while self.driver.current_url == self.login_url:
				# whether verify code exist
				try:
					self.wait.until(lambda the_driver: the_driver.find_element_by_id('door').is_displayed())
				except:
					raise Exception('login failed, confirm your email or password')

				# enter verify code manually
				self.driver.save_screenshot('verified_code.png') # screen shot for input manually
				code = raw_input('[INPUT ] Enter verified code: \n')
				code_input = self.driver.find_element_by_id('door')
				code_input.clear()
				for c in code:
					code_input.send_keys(c)
				self.driver.find_element_by_css_selector('input.W_btn_a').click()  # submit
				time.sleep(self.short)

		return

	def __login_by_cookie(self):
		'''
		login by cookie
		'''
		print self.title, 'login by cookies...'
		# get cookie
		cookie = {}
		try:
			with open('cookies\\%s.pkl' % self.cookie) as pkl_file:
				cookie = pickle.load(pkl_file)
		except IOError:
			raise Exception('cookie file not exists')

		# index
		self.driver.get(self.cookie_login_url)
		# set cookie
		self.driver.add_cookie(cookie)

		self.driver.refresh()

		# check login status
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_class_name("user-name").is_displayed())
		except:
			raise Exception('invalid cookie')

		self.username = self.driver.find_element_by_class_name("user-name").text

		return

	def __can_answer(self, url):
		'''
        is this question can be answered
        :return: boolean
        '''
		# print  self.title, 'opening question page'
		self.driver.get(url)

		# whether adopted
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('.wgt-best').is_displayed() or \
											   the_driver.find_element_by_id('wgt-myanswer').is_displayed())
		except:
			return True

		return False

	def comment(self, url, content):
		'''
		post message
		:param contents: list
		:return: 
		'''
		print self.title, 'opening comment page ...'
		self.driver.get(url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('.answer-last span.comment').is_displayed())
		except:
			raise Exception('redirect failed')

		# enter message
		print  self.title, 'post comment ...'
		# click '回复' to open textarea
		self.driver.find_element_by_css_selector('.answer-last span.comment').click()
		# wait and enter text
		time.sleep(self.short)
		txt_input = self.driver.find_element_by_css_selector('.answer-last textarea')
		txt_input.clear()
		for c in content:
			txt_input.send_keys(c)
		# wait and submit by CTRL+ENTER
		time.sleep(self.short)
		txt_input.send_keys(Keys.CONTROL, Keys.ENTER)

		# wait and screen shot
		time.sleep(self.short)
		# self.driver.save_screenshot('comment_success.png')

		print  self.title, 'post comment success'
		return

	def answer(self, url, content, anonymous=False):
		'''
		post message
		:param contents: list
		:return: bool
		'''

		if not self.__can_answer(url):
			raise Exception('this question has been solved or answered')

		print self.title, 'post answer'
		try:
			# 0 answer: button with text '提交回答'
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('#answer-editor .new-editor-deliver-btn').is_displayed())
		except:
			# > 0 answer and I have not answered this question" button with text '我有更好答案'
			try:
				self.wait.until(lambda the_driver: the_driver.find_element_by_id('answer-bar').is_displayed())
			except:
				raise Exception('redirect failed')

			self.driver.find_element_by_id('answer-bar').click()
			time.sleep(self.short)


		# enter message
		# choice I: send_keys()
		#
		# self.driver.switch_to.frame('ueditor_0')
		# txt_input = self.driver.find_element_by_tag_name('body')
		# txt_input.clear()
		# for c in content:
		# 		txt_input.send_keys(c)
		# wait and submit
		# time.sleep(self.short)
		# self.driver.switch_to.default_content()
		# btn = self.driver.find_element_by_css_selector('#answer-editor .new-editor-deliver-btn')
		# btn.click()

		# however, sending keys for a non-input element such as 'BODY' does not work for PhantomJS
		# even though it works well for Chrome or FireFox
		# here comes choice II: execute_script()

		js = "document.getElementById('ueditor_0').contentWindow.\
			document.getElementsByTagName('body')[0].innerHTML = ' % s'" % content
		self.driver.execute_script(js)
		# wait and submit
		time.sleep(self.short)
		if anonymous:
			self.driver.find_element_by_css_selector('.unname input').click() # anonymous
		btn = self.driver.find_element_by_css_selector('#answer-editor .new-editor-deliver-btn')
		btn.click()

		# wait for results
		time.sleep(self.long)

		if self.driver.find_element_by_css_selector('span.answer-title').text == u'我的回答':
			return True
		else:
			self.driver.save_screenshot('answer_failed.png')
			return False

	def down(self):
		print self.title, 'quit ...'
		self.driver.quit()

if __name__ == '__main__':

	url = "https://zhidao.baidu.com/question/1371976507250043259.html"
	content1 = '<p>paragraph 1</p><p>paragraph 2</p>'
	content2 = 'something comment'

	S = IAnswer(browser=1, cookie=u'buptzym')
	# S.answer(url, content1)
	# S.comment(url, content2)
	# S.down()












