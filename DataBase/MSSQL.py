# coding=utf-8
import pyodbc
import traceback


database_client_connection = None
database_client_cursor = None

def build_connection():
    global database_client_connection, database_client_cursor
    try:
        if database_client_connection:
            database_client_connection.close()
    except Exception, e:
        traceback.print_exc(e)
    try:
        database_client_connection = pyodbc.connect('DRIVER={SQL SERVER};SERVER=172.16.0.26;DATABASE=pachong;UID=likai;PWD=d!{<kN5K38u-')
        database_client_cursor = database_client_connection.cursor()
    except Exception, e:
        traceback.print_exc(e)
        build_connection()

build_connection()


def execute_update(sql):
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

