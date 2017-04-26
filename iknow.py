# encoding: utf8

import random, time
import ifinder, isolver, ianswer

class IKNOW:
    def __init__(self, num=10, browser=0, method='site', cookie=''):
        '''
        init parameters
        :param keyword: 
        :param browser: 
        :param cookie: 
        '''
        self.title = '[IKNOW ] '
        print self.title, 'RUN...'

        self.target = num    # questions to be answered
        self.success = 0     # questions answered

        # application stops if failed continuously
        self.target_failed = 5
        self.failed = 0

        # init components
        self.finder = ifinder.IFinder()
        self.solver = isolver.ISolver(method=method)
        self.answer = ianswer.IAnswer(browser=browser, cookie=cookie)

        return

    def run(self, tag=u'百度', site=2):
        '''
            post answer automatically
        '''
        while self.success < self.target and self.failed < self.target_failed:
            print

            # question
            try:
                this_question = self.finder.get_question(tag)
            except Exception as msg:
                print '[ERROR ] ', msg
                self.failed += 1
                continue

            # solver
            try:
                content = self.solver.solver(keyword=this_question[1], site=site)
            except Exception as msg:
                print '[ERROR ] ', msg
                self.failed += 1
                continue

            # post answer
            res = False
            try:
                res = self.answer.answer(this_question[0], content)
            except Exception as msg:
                print '[ERROR ] ', msg

            # results
            if res:
                self.success += 1
                self.failed = 0    # clear failed times
                print self.title, 'post answer successfully'
                time.sleep(random.randint(100, 250)) # delay for 1-2 minutes
            else:
                self.failed += 1
                print self.title, 'post answer failed'

        self.down()

        return

    def down(self):
        # summary
        print
        self.answer.down()
        print
        print self.title, "target number: %d, succeed: %d" % (self.target, self.success)
        print self.title, "END"

if __name__ == '__main__':

    I = IKNOW(num=5, browser=0, cookie=u'buptzym')
    I.run(tag=u'高等数学', site=2)