# coding=utf-8

import PackageTool
from database import MSSQL
from TimeUtils import *
import json
from Searcher import Searcher
from bs4 import BeautifulSoup
import MySQLdb
import os
import sys


mysql = MSSQL()


class ChongQingSearcher(Searcher):
    def __init__(self):
        super(ChongQingSearcher, self).__init__()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
                        "Host": "gsxt.cqgs.gov.cn",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Connection": "keep-alive",
						"Referer": "http://gsxt.cqgs.gov.cn/search_tojyyc.action",
						"X-XSRF-TOKEN": "89000"
                        }

    def set_config(self):
		self.add_proxy()

    def update_proc(self):
		url = "http://gsxt.cqgs.gov.cn/search_searchjyyc.action"
		self.num_path = os.path.join(sys.path[0], '../ChongQing/num.txt')
		num_path = self.num_path
		while True:
			with open(num_path, 'rb') as f:
				num = int(f.read())
				f.close()
			params = {"currentpage": num,'itemsperpage': '10'}
			r = self.post_request(url=url, params=params)
			r_text = r.text
			body_text = r_text[r_text.index('['):r_text.rindex(']')+1]
			json_dict = json.loads(body_text)
			for company_text in json_dict:
				credit_no = ''
				regno = ''
				if '_name' in company_text:
					ent_name = company_text['_name']
				if '_regCode' in company_text:
					regno = company_text['_regCode']
				if '_creditcode' in company_text:
					credit_no = company_text['_creditcode']
				self.province = u'重庆市'
				sql = "insert into Business_Abnormal values('%s','%s','%s','%s',now())" % (ent_name, self.province, regno, credit_no)
				print sql
				mysql.execute(sql)
			mysql.commit()
			print u'第%s页更新完成' % num
			num += 1
			with open(num_path, 'wb') as f:
				f.write(str(num))
				f.close()


if __name__ == '__main__':
    update_searcher = ChongQingSearcher()
    update_searcher.update_proc()

