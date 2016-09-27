# coding=utf-8

import mysql.connector
import traceback

class MYSQL(object):

	database_client_connection = None
	database_client_cursor = None

	def __init__(self):
		config={'host':'172.16.0.20', #默认172.16.0.20
				'user':'qianjing',
				'password':'zxcASDqwe!@#',
				'port':'3306' ,#默认即为3306
				'database':'enterprise_name',
				'charset':'utf8'#默认即为utf8
				}
		# try:
		#   database_client_connection = mysql.connector.connect(**config)
		#   database_client_cursor = database_client_connection.cursor()
		# except mysql.connector.Error as e:
		#   print('connect fails!{}'.format(e))

	def build_connection(self):
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

	def excute_update(self,sql):
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
	pass