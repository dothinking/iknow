# encoding=utf8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time, pickle


class IAnswer:

	def __init__(self ):
		'''
		init driver
		:param cookie: pickle name for cookie
		:param browser: 1 chrome, others phantomjs
		'''
		self.title = '[ANSWER] '
		print(self.title, 'init driver...\n')

		# login url
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
			'userAgent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
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

		self.driver = webdriver.PhantomJS(service_args=service_args)

		# set browser size
		# to fix bug 'Element is not currently visible and may not be manipulated'
		self.driver.maximize_window()

		# waiting time
		self.wait = WebDriverWait(self.driver, 5)
		self.short = 3
		self.long = 10
		return

	def check_cookie(self, cookie):
		'''
		login by cookie
		'''
		print(self.title, 'check cookie...')
		self.driver.get(self.cookie_login_url)
		self.driver.add_cookie(cookie)
		self.driver.refresh()

		# check login status
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_class_name("user-name").is_displayed())
		except:
			self.username = ''
			return False

		self.username = self.driver.find_element_by_class_name("user-name").text
		return True

	def down(self):
		print(self.title, 'quit ...')
		self.driver.quit()

if __name__ == '__main__':

	cookies = [
		{
			'path' : '/',
			'domain':'.baidu.com',
			'name':'BDUSS',
			'value' : '095WUo4VVctaHhVM2VTaW9hZDBYSDBMVlpUYUZBbFF-S2F3VGYxZXUyNTMxSHBZSVFBQUFBJCQAAAAAAAAAAAEAAABGR5Ibsa-QxT2h3RW9qMU5WVm9MWU9tNm5hfmZZU2VPMFhXVUhhd2Z5bU5mZmxybWlCbjlVQVFBQUFBJCQAAAAAAAAAAAEAAABZ0NELbGlmYW5neHZhAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKJ5V1SieVdUNG',
			'expiry':1751370498
		},{
			'path' : '/',
			'domain':'.baidu.com',
			'name':'BDUSS',
			'value' : '85TmQyZ350VmdLN0gxdjVldjBvVUN-Ec4NWtsYlF5c045Q2hFTmxOVnNyanFJSlVhc1F2S29kSkVleFZpcUVFbnlOR1ZSQVFBQUFBJCQAAAAAAAAAAAEAAADF6f0MeXVoYW44MjM5Mjg4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPKnPVHypz1RO',
			'expiry':1751370498
		}
	]

	i = 1
	S = IAnswer()
	for cookie in cookies:
		if S.check_cookie(cookie):
			output = open('%s.pkl' % S.username, 'w')
			pickle.dump(cookie, output)
			output.close()
			print(S.title, 'login success, welcome %s' % S.username)
		else:
			print(S.title, 'invalid cookie')

		i += 1
		print()
	S.down()











