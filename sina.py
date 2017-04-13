# encoding=utf8  

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import sys
from time import sleep

class SINA:

	def __init__(self):
		'''
		init driver
		'''
		print 'init driver...'
		# 1 header
		# userAgent is set in phantomjs.page.settings.userAgent instead of phantomjs.page.customHeaders
		headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
		    'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
			'cookie': 'SINAGLOBAL=3047146166209.1313.1457599214582; wb_publish_fist100_2366509262=1; login_sid_t=fab2b095e7c4170ed7c53759e6af10bf; YF-Ugrow-G0=56862bac2f6bf97368b95873bc687eef; YF-V5-G0=7a7738669dbd9095bf06898e71d6256d; _s_tentry=-; Apache=4017888237212.519.1492052648193; ULV=1492052648201:40:2:2:4017888237212.519.1492052648193:1491810946222; YF-Page-G0=3d55e26bde550ac7b0d32a2ad7d6fa53; wvr=6; ULOGIN_IMG=14920588483177; UOR=www.doc88.com,widget.weibo.com,www.liaoxuefeng.com; WBtopGlobal_register_version=a05309c5d15974a8; SCF=AtCkFMp1nu3XsiELH7dVoXyIBAEDJ6uMptRLXnZQOSWu0C3Ar0UJ6NcrbPSwXXfNHqCwe2zMWFtELiTUmWvtayE.; SUB=_2A25160o9DeThGeRN7VQU8CfOzT6IHXVWgTz1rDV8PUNbmtANLVL4kW8-99PVqj4M9FURvWZob-GJlHqgHw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF.5unk0d6Y3Sjz-XGQVuh85JpX5K2hUgL.Foz0Soqfeh.ESoz2dJLoI7D0INLNqP.Eeh2E; SUHB=0btt72v3CEDFCw; ALF=1492677867; SSOLoginState=1492073069; un=train8808@gmail.com',
		}

		for key, value in headers.iteritems():
			DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

		DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

		# 2 service_args
		service_args = [
			'--load-images=false'
			# '--proxy=127.0.0.1:9999',
			#  '--proxy-type=http',
			#  '--ignore-ssl-errors=true'
		]

		self.driver = webdriver.PhantomJS(service_args=service_args)
		# self.driver = webdriver.Firefox()


		# 3 set browser size
		# to fix bug 'Element is not currently visible and may not be manipulated'
		self.driver.maximize_window()

		# waiting time
		self.wait = WebDriverWait(self.driver, 10)

		# login url & post url
		self.login_url = "https://login.sina.com.cn/signup/signin.php"
		self.post_url = "http://weibo.com/"

		return


	def login_by_username(self, username, password):
		'''
		login
		:param username: 
		:param password: 
		:return: 
		'''
		print 'login...'

		# load login page
		self.driver.get(self.login_url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_id('username').is_displayed())
		except:
			self.driver.quit()
			print 'load login page failed'
			sys.exit(0)

		# fill form and submit
		username_input = self.driver.find_element_by_id('username')  # email
		username_input.clear()
		for c in username: # avoid incomplete input
			username_input.send_keys(c)
		print 'username done'

		pswd_input = self.driver.find_element_by_id('password')  # password
		pswd_input.clear()
		for c in password:
			pswd_input.send_keys(c)
		print 'password done'

		self.driver.find_element_by_css_selector('input.W_btn_a').click()  # submit

		try:
			self.wait.until(lambda the_driver: the_driver.current_url != self.login_url)
		except:
			self.driver.quit()
			print 'login failed'
			sys.exit(0)

		print 'login success'

		# attention !!
		# waiting for redirection and complete login
		sleep(3)
		return

	def login_by_cookies(self):
		'''
		login
		:return: 
		'''
		print 'login...'
		# load login page
		self.driver.get(self.post_url)
		# set cookie
		cookies = {
			'ULV' : '1492074787742:1:1:1::',
			'SINAGLOBAL' : '116.228.198.3_1492052568.304730',
			'bdshare_firstime' : '1492074787336',
			'UOR' : ',my.sina.com.cn,',
			'WEB2' : '697ab7c7921742370c82df9cf770979d',
			'U_TRS2' : '00000022.ec326f2.58ef4125.22df2e27',
			'U_TRS1' : '00000022.eb426f2.58ef4125.e75339d8',
			'sso_info' : 'v02m6alo5qztZScpoWpm6OguIyDoKadlqWkj5OIs42jmLWMg6SyjaOIwA==',
			'ALF' : '1523610787',
			'SUBP' : '0033WrSXqPxfM725Ws9jqgMF55529P9D9WF.5unk0d6Y3Sjz-XGQVuh85NHD95QEe0qcSK54eoqEWs4DqcjZMc_4Uc84eo5pentt',
			'SUB' : '_2A2516zFzDeThGeRN7VQU8CfOzT6IHXVWgSW7rDV_PUNbm9AKLRSlkW8Mdt4K0zMaKrXS9rWXPKGiED0S1g..',
			'SCF' : 'AjCGf5jxsWa54Bno3z5-4cveHpByqGino-6xTPpu-nQXjv6gffdefSEn7o3WRCAPlsEQun6HefCDROfZnTjVrY4.',
		}
		for name, value in cookies.items():
			self.driver.add_cookie({
				'name'  : name,
				'value' : value
			})

		print 'login success'

		cookie = "; ".join([item["name"] + "=" + item["value"] +"\n" for item in self.driver.get_cookies()])
		print cookie

		# attention !!
		# waiting for redirection and complete login
		sleep(3)
		return

	def post(self, content):
		'''
		post message
		:param content: 
		:return: 
		'''
		# print cookies
		cookie = "; ".join([item["name"] + "=" + item["value"] +"\n" for item in self.driver.get_cookies()])
		print cookie
		print 'redirect to post url ...'
		self.driver.get(self.post_url)
		try:
			self.wait.until(lambda the_driver: the_driver.find_element_by_css_selector('textarea.W_input').is_displayed())
		except:
			self.driver.quit()
			print 'redirect failed'
			sys.exit(0)

		# enter message
		print 'post message ...'
		txt_input = self.driver.find_element_by_css_selector('textarea.W_input')
		txt_input.clear()
		for c in content:
			txt_input.send_keys(c)

		sleep(2) # waiting for submit

		self.driver.find_element_by_css_selector('.func>a').click() # submit

		sleep(3)
		self.driver.save_screenshot('post_message.png')

		print 'post message success'
		return

	def down(self):
		print 'quit ...'
		self.driver.quit()

S = SINA()
# S.login_by_username('train8808@gmail.com', 'password')
# S.login_by_cookies()
S.post(u'来自Selenium与PhantomJS的测试消息。')
S.down()






