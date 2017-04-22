# encoding: utf8
import sqlite3
import random

class ISolver:
    def __init__(self):

        self.title = '[SOLVER] '
        print self.title, 'init question solver...'
        return

    def solver_1(self, dbName='poetry'):
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

        print self.title, 'answer: %s' % content

        return content