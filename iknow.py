# encoding=utf8  

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import sys
from time import sleep
import pickle

class IKNOW:

	def __init__(self, cookie=''):
		'''
		init driver
		'''
		print '* init driver...'
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

		self.driver = webdriver.PhantomJS(service_args=service_args)
		# self.driver = webdriver.Chrome()


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
		if(self.cookie):
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
		# get cookie
		cookie = {}
		try:
			pkl_file = open(self.cookie + '.pkl')
			cookie = pickle.load(pkl_file)
		except Exception as err:
			print "  cookie file not exists: " + str(err)
			self.driver.quit()
			print '  login failed.'
			sys.exit(0)
		pkl_file.close()

		# index
		self.driver.get(self.cookie_login_url)
		# set cookie
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
			# button '提交回答'
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('#answer-editor .new-editor-deliver-btn').is_displayed())
		except:
			# button '我有更好答案'
			try:
				self.wait.until(lambda the_driver: the_driver.find_element_by_id('answer-bar').is_displayed())
			except:
				self.driver.quit()
				print '  redirect failed'
				sys.exit(0)

			self.driver.find_element_by_id('answer-bar').click()
			sleep(1)


		# enter message

		print '* post answer ...'
		# choice I: send_keys()
		#
		# self.driver.switch_to.frame('ueditor_0')
		# txt_input = self.driver.find_element_by_tag_name('body')
		# txt_input.clear()
		# for c in content:
		# 		txt_input.send_keys(c)
		# wait and submit
		# sleep(3)
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
		sleep(2)
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



# cookie = {}
url = "https://zhidao.baidu.com/question/1371976507250043259.html"

content = u'<p>你连题目都没有给出，这可如何讲解？</p><p>高斯定理将第二类曲面积分转换为三重积分，所以如果不用高斯积分，那就按照普通的曲面积分的基本做法解题就行了。</p>'


S = IKNOW('cookie-3')

S.login()

# S.answer(url, content)

# S.comment(comment_url, u"这回复的啥呀？")
#
S.down()









