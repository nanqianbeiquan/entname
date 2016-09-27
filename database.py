# coding=gbk

import pyodbc
import MySQLdb


class MSSQL(object):

    # def __init__(self):
    #     self.connection = pyodbc.connect('DRIVER={MySQL ODBC 5.3 Driver};'
    #                                      'SERVER=172.16.0.20;'
    #                                      'PORT = 3306;'
    #                                      'DATABASE=enterprise_name;'
    #                                      'User = qianjing; '
    #                                      'password = zxcASDqwe!@#')
    #     # self.connection = pyodbc.connect('Data Source Name=172.16.0.20;User=qianjing;Password=zxcASDqwe!@#')
    #     self.cursor = self.connection.cursor()
    def __init__(self):
    # def connection(self):
        self.conn = MySQLdb.connect(host='172.16.0.20',port=3306,user='zhangxiaogang',passwd='gangxiaozhang',db='enterprise_name',charset='utf8')
        self.cursor = self.conn.cursor()

    def execute(self, query):
        self.cursor.execute(query)

    def commit(self):
        self.conn.commit()
