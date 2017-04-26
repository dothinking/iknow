# encoding: utf8
import sqlite3
import requests
from bs4 import BeautifulSoup
import random

class ISolver:
    def __init__(self, method='site'):
        '''
        initialization
        :param method: 
            db   : provide random answer from database
            site : search answer from website
        '''
        self.title = '[SOLVER] '
        self.method = method
        print self.title, 'init question solver...'

        if self.method == 'site':
            self.base_url = "https://www.baidu.com/s"
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.5 Safari/537.36',
                'Referer': 'https://www.baidu.com'
            }

        return

    def solver(self, keyword=r'百度', site=1):
        '''
        solver
        : param site:
            1 zhidao.baidu.com
            2 zybang.com
        :return: 
        '''
        if self.method == 'db':
            content = self.__solver_from_db()
        elif self.method == 'site':
            content = self.__solver_from_site(keyword, site)

        return content

    def __solver_from_db(self, dbName='poetry'):
        '''
        generate answer from sqlite records
        :param dbName: 
        :return: 
        '''
        # database connection
        con = sqlite3.connect('poetry\\%s.db' % dbName)
        cur = con.cursor()

        # count
        cur.execute("SELECT COUNT(ID) FROM " + dbName)
        num = cur.fetchone()[0]

        # query randomly
        id = random.randint(1, num)
        cur.execute('SELECT CONTENT FROM %s WHERE ID=?' % dbName, (id,))

        # results
        content = cur.fetchone()[0]
        cur.close()
        con.close()

        content = '<p>' + content.replace(u'。', u'。' + '</p><p>').replace(u'？', u'？' + '</p><p>')
        print self.title, 'answer: %s' % content
        return content

    def __get_content(self, url, site):
        # go to destination page
        if site == 1:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "lxml")
            answer = soup.select("#good-answer dd span")

            # filter data
            content = ''
            if answer:
                for item in answer[0].stripped_strings:
                    content += r'<p>%s</p>' % repr(item)
        else:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "lxml")
            answer = soup.select("#good-answer dd span")

            # filter data
            content = ''
            if answer:
                for item in answer[0].stripped_strings:
                    content += '<p>%s</p>' % item

        return content

    def __solver_from_site(self, keyword, site):
        '''
        searching answer from site by baidu engine 
        :param keyword: 
        :param site: 
        :return: 
        '''
        # searching parameters
        if site == 1:
            website = 'zhidao.baidu.com'
        else:
            website = 'zybang.com'

        str = r'%s site:%s' % (keyword, website)
        param = {
            'wd': str,
            'ie': 'utf8'
        }
        # get searching page
        response = requests.get(self.base_url, params=param, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")

        # get content
        num = 1
        url = soup.select("#1 .t a")[0]['href']
        content = self.__get_content(url, site)

        while not content and num < 8:
            num += 1
            url = soup.select(r"#%d .t a" % num)[0]['href']
            content = self.__get_content(url, site)

        if not content:
            raise Exception('can not find answer')

        print self.title, 'answer: %s' % content
        return content


if __name__ == '__main__':

    F = ISolver()
    F.solver(keyword=r'三重积分', site=2)