# coding=utf-8

import mysql.connector
import traceback


database_client_connection = None
database_client_cursor = None

def build_connection():
	config = {'host':'172.16.0.20',#服务器地址
			  'user':'qianjing',#数据库账号
			  'password':'zxcASDqwe!@#',#数据库密码
			  'port':'3306',#默认3306
			  'database':'enterprise_name',#数据库名
			  'charset':'utf8',#默认utf8

	}
	global database_client_connection, database_client_cursor
	try:
		if database_client_connection:
			database_client_connection.close()
	except Exception, e:
		traceback.print_exc(e)
	try:
		database_client_connection = mysql.connector.connect(**config)
		database_client_cursor = database_client_connection.cursor()
	except Exception, e:
		traceback.print_exc(e)
		build_connection()

build_connection()

def excute_update(sql):
	global database_client_connection, database_client_cursor
	try:
		database_client_cursor.execute(sql)
		database_client_connection.commit()
	except Exception, e:
		traceback.print_exc(e)
		build_connection()
		execute_update(sql)

def execute_query(sql):
	global database_client_connection, database_client_cursor
	try:
		database_client_cursor.execute(sql)
		return database_client_cursor.fetchall()
	except Exception, e:
		traceback.print_exc(e)
		build_connection()
		return execute_query(sql)

if __name__ == '__main__':
	sql = "insert into SpotCheck values('%s','%s','%s','%s',now())" % ('文昌展宏水产专业合作社', '海南省', '', '469005NA000091X')
	print sql
	excute_update(sql)