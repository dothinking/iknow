# encoding: utf8

import random, time
import ifinder, isolver, ianswer

class IKNOW:
    def __init__(self, num=10, keyword=u'百度', browser=0, cookie=''):
        '''
        init parameters
        :param keyword: 
        :param browser: 
        :param cookie: 
        '''
        self.title = '[IKNOW ] '
        print self.title, 'RUN...'

        self.keyword = keyword
        self.target = num    # questions to be answered
        self.success = 0     # questions answered

        # application stops if failed continuously
        self.target_failed = 5
        self.failed = 0

        # init components
        self.finder = ifinder.IFinder()
        self.solver = isolver.ISolver()
        self.answer = ianswer.IAnswer(browser=browser, cookie=cookie)

        return

    def run(self):
        '''
            post answer automatically
        '''
        while self.success < self.target and self.failed < self.target_failed:
            print

            # question
            try:
                url = self.finder.get_question(self.keyword)
            except Exception as msg:
                print '[ERROR ] ', msg
                self.down()

            # solver
            content = self.solver.solver_1()
            html_content = '<p>' + content.replace(u'。', u'。' + '<p>').replace(u'？', u'？' + '<p>')

            # post answer
            res = False
            try:
                res = self.answer.answer(url, html_content)
            except Exception as msg:
                print '[ERROR ] ', msg

            # results
            if res:
                self.success += 1
                self.failed = 0    # clear failed times
                print self.title, 'post answer successfully'
                time.sleep(random.randint(60, 120)) # delay for 1-2 minutes
            else:
                self.failed += 1
                print self.title, 'post answer failed'

        self.down()

        return

    def down(self):
        # summary
        self.answer.down()
        print
        print self.title, "target number: %d, succeed: %d" % (self.target, self.success)
        print self.title, "END"

if __name__ == '__main__':

    I = IKNOW(num=6, keyword=u'诗词', browser=0, cookie=u'爵丶士丶')
    I.run()