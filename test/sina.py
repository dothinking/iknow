# encoding=utf8  

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import sys
from time import sleep

class SINA:

	''' login sina weibo and post message'''

	def __init__(self, cookie):
		'''
		init driver
		'''
		print 'init driver...'
		self.cookie = cookie
		# header
		headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
			'Connection': 'keep-alive',
			'cookie': self.cookie,
		}
		for key, value in headers.iteritems():
			DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

		# setting
		settings = {
			'userAgent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
			# 'loadImages': False
		}
		for key, value in settings.iteritems():
			DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.{}'.format(key)] = value

		# DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

		# service_args
		service_args = [
			# '--load-images=false'
			# '--proxy=127.0.0.1:9999',
			#  '--proxy-type=http',
			#  '--ignore-ssl-errors=true'
		]

		self.driver = webdriver.PhantomJS(service_args=service_args)
		# self.driver = webdriver.Chrome()


		# set browser size
		# to fix bug 'Element is not currently visible and may not be manipulated'
		self.driver.maximize_window()

		# waiting time
		self.wait = WebDriverWait(self.driver, 5)

		# login url & post url
		self.login_url = "https://login.sina.com.cn/signup/signin.php"
		self.post_url = "http://weibo.com/"

		return


	def login(self):
		'''
		login
		:param username: 
		:param password: 
		:return: 
		'''
		print 'login...'

		# load login page
		self.driver.get(self.login_url)

		# if cookie is null, login by username
		if(self.cookie == ''):
			try:
				self.wait.until(lambda the_driver: the_driver.find_element_by_id('username').is_displayed())
			except:
				self.driver.quit()
				print 'load login page failed'
				sys.exit(0)

			username = raw_input('Enter login email:\n')
			password = raw_input('Enter password:\n')

			# fill form and submit
			username_input = self.driver.find_element_by_id('username')  # email
			username_input.clear()
			for c in username: # avoid incomplete input
				username_input.send_keys(c)

			pswd_input = self.driver.find_element_by_id('password')  # password
			pswd_input.clear()
			for c in password:
				pswd_input.send_keys(c)

			self.driver.find_element_by_css_selector('input.W_btn_a').click()  # submit

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

		# finally, login success
		# attention! waiting for redirection and complete login
		print 'login success'
		sleep(3)

		return

	def post(self, contents):
		'''
		post message
		:param contents: list
		:return: 
		'''
		print 'redirect to post url ...'
		self.driver.get(self.post_url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('.limits + a').is_displayed())
		except:
			self.driver.quit()
			print 'redirect failed'
			sys.exit(0)

		# print cookies
		# cookie = "; ".join([item["name"] + "=" + item["value"] + "\n" for item in self.driver.get_cookies()])
		# print cookie

		# enter message
		txt_input = self.driver.find_element_by_css_selector('textarea.W_input')
		btn = self.driver.find_element_by_css_selector('.limits + a')
		i = 1
		for content in contents:
			print 'post message ' + str(i)
			txt_input.clear()
			for c in content:
				txt_input.send_keys(c)
			# waiting for a moment and then submit
			sleep(2)
			btn.click() # submit

			sleep(3)
			self.driver.save_screenshot('post_success_'+str(i)+'.png')

			i += 1

		print 'post message success'
		return

	def down(self):
		print 'quit ...'
		self.driver.quit()


cookie = ''

S = SINA(cookie)

S.login()

S.post([
	u'来自Selenium与PhantomJS的测试消息1。',
	u'来自Selenium与PhantomJS的测试消息2。',
	u'来自Selenium与PhantomJS的测试消息3。'
])

S.down()







