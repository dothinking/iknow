# encoding=utf8  

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import sys
from time import sleep

class IKNOW:

	def __init__(self, cookies = {}):
		'''
		init driver
		'''
		print '* init driver...'
		self.cookies = cookies
		# login url
		self.login_url = "https://passport.baidu.com/v2/?login"
		self.cookie_login_url = "https://www.baidu.com"

		# header
		headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
			'Connection': 'keep-alive',
		}
		for key, value in headers.items():
			DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

		# setting
		settings = {
			'userAgent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
			'loadImages': False
		}
		for key, value in settings.items():
			DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.{}'.format(key)] = value

		# service_args
		service_args = [
			# '--load-images=false'
			# '--proxy=127.0.0.1:9999',
			#  '--proxy-type=http',
			#  '--ignore-ssl-errors=true'
		]

		# self.driver = webdriver.PhantomJS(service_args=service_args)
		self.driver = webdriver.Chrome()


		# set browser size
		# to fix bug 'Element is not currently visible and may not be manipulated'
		self.driver.maximize_window()

		# waiting time
		self.wait = WebDriverWait(self.driver, 5)

		return

	def login(self):
		'''
		login
		'''
		# if cookie is null, login by username
		if(self.cookies):
			self.login_by_cookie()
		else:
			self.login_by_username()

		# finally, login success
		print '  login success'
		print '********************************'
		print '  welcome ' + self.username
		# print cookies
		# print self.driver.get_cookies()
		sleep(3) # attention! waiting for redirection and complete login

		return

	def login_by_username(self):
		'''
		login by username
		'''
		print '* login by username...'
		# load login page
		self.driver.get(self.login_url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_id('TANGRAM__PSP_3__submit').is_displayed())
		except:
			self.driver.quit()
			print '  load login page failed'
			sys.exit(0)

		username = raw_input('  enter username:\n')
		password = raw_input('  enter password:\n')

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
			self.driver.save_screenshot('login.png')
			# login failed, check verify code
			# considering mistaking input, while loop is used
			while self.driver.current_url == self.login_url:
				# whether verify code exist
				try:
					self.wait.until(lambda the_driver: the_driver.find_element_by_id('door').is_displayed())
				except:
					self.driver.quit()
					print 'login failed, confirm your email or password'
					sys.exit(0)

				# enter verify code manually
				self.driver.save_screenshot('verified_code.png') # screen shot for input manually
				code = raw_input('Enter verified code: \n')
				code_input = self.driver.find_element_by_id('door')
				code_input.clear()
				for c in code:
					code_input.send_keys(c)
				self.driver.find_element_by_css_selector('input.W_btn_a').click()  # submit
				sleep(2)

		return


	def login_by_cookie(self):
		'''
		login by cookie
		'''
		print '* login by cookies...'
		# index
		self.driver.get(self.cookie_login_url)
		# set cookie
		for cookie in self.cookies:
			self.driver.add_cookie(cookie)

		self.driver.refresh()

		# check login status
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_class_name("user-name").is_displayed())
		except:
			self.driver.quit()
			print '  login failed.'
			sys.exit(0)

		self.username = self.driver.find_element_by_class_name("user-name").text

		return

	def comment(self, url, content):
		'''
		post message
		:param contents: list
		:return: 
		'''
		print '* opening comment page ...'
		self.driver.get(url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('.answer-last span.comment').is_displayed())
		except:
			self.driver.quit()
			print '  redirect failed'
			sys.exit(0)

		# enter message
		print '* post comment ...'
		# click '回复' to open textarea
		self.driver.find_element_by_css_selector('.answer-last span.comment').click()
		# wait and enter text
		sleep(1)
		txt_input = self.driver.find_element_by_css_selector('.answer-last textarea')
		txt_input.clear()
		for c in content:
			txt_input.send_keys(c)
		# wait and submit by CTRL+ENTER
		sleep(3)
		txt_input.send_keys(Keys.CONTROL, Keys.ENTER)

		# wait and screen shot
		sleep(1)
		self.driver.save_screenshot('comment_success.png')

		print '  post comment success'
		return

	def answer(self, url, content):
		'''
		post message
		:param contents: list
		:return: 
		'''
		print '* opening question page ...'
		self.driver.get(url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('#answer-editor .new-editor-deliver-btn').is_displayed())
		except:
			self.driver.quit()
			print '  redirect failed'
			sys.exit(0)

		# enter message

		print '* post answer ...'
		self.driver.switch_to.frame('ueditor_0')
		txt_input = self.driver.find_element_by_tag_name('body')
		txt_input.clear()
		for c in content:
			if c == '#':
				txt_input.send_keys(Keys.ENTER)
			else:
				txt_input.send_keys(c)
		# wait and submit
		sleep(3)
		self.driver.switch_to.default_content()
		btn = self.driver.find_element_by_css_selector('#answer-editor .new-editor-deliver-btn')
		btn.click()

		# wait and screen shot
		sleep(1)
		self.driver.save_screenshot('answer_success.png')

		print '  post answer success'
		return

	def down(self):
		print '* quit ...'
		self.driver.quit()


cookie = [{
		'name'  : 'BDUSS',
		# 'value' : 'E41M0tUZHNFbUx1QldXdWxlalFTT3o5VThUUThlM1VOQkhZUXJyYkZLcjVhRVZZSVFBQUFBJCQAAAAAAAAAAAEAAABmVuJWd2VibWFzdGVydnBzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPnbHVj52x1YO',
		'value' : 'C1DSUZMTFo0cE1td0taejhSczI4VXRtRkxzR2N0NU9vM1hWV1JzM2IxcjJ5eXRZSVFBQUFBJCQAAAAAAAAAAAEAAAAxkTMAZGVtb24xMTkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPY-BFj2PgRYU',
		'domain': '.baidu.com',
		'expiry': 1751370498,
		'path'  : '/'
}]

# cookie = {}
url = "https://zhidao.baidu.com/question/429634604807320052.html"

content = u'彼黍离离，彼稷之苗。行迈靡靡，中心摇摇。#\
知我者谓我心忧，不知我者谓我何求。#\
悠悠苍天！此何人哉？##\
彼黍离离，彼稷之穗。行迈靡靡，中心如醉。#\
知我者谓我心忧，不知我者谓我何求。#\
悠悠苍天！此何人哉？##\
彼黍离离，彼稷之实。行迈靡靡，中心如噎。#\
知我者谓我心忧，不知我者谓我何求。#\
悠悠苍天！此何人哉？'



S = IKNOW(cookie)

S.login()

S.answer(url, content)

# S.comment(comment_url, u"这回复的啥呀？")
#
S.down()









