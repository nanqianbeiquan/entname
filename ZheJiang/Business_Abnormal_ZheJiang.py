# coding=utf-8

import PackageTool
from DataBase.MYSQL import *
from TimeUtils import *
import json
from ba.Searcher import Searcher
from bs4 import BeautifulSoup
import MySQLdb
import os
import sys


# mysql = MSSQL()


class ZheJiangSearcher(Searcher):
    def __init__(self):
        super(ZheJiangSearcher, self).__init__(use_proxy=True, lock_ip=False)
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
		url = "http://gsxt.zjaic.gov.cn/unusualcatalog/doReadUnusualCatalogListJSON.do"
		self.num_path = os.path.join(sys.path[0], '../ZheJiang/num.txt')
		num_path = self.num_path
		while True:
			with open(num_path, 'rb') as f:
				num = int(f.read())
				f.close()
			params = {"pagination.currentPage": num,'pagination.pageSize': '10'}
			r = self.post_request(url=url, params=params)
			r_text = r.text
			if u']' not in r_text:
				continue
				# r_text = r_text + '}]'
			body_text = r_text[r_text.index('['):r_text.rindex(']')+1]
			json_dict = json.loads(body_text)
			for company_text in json_dict:
				credit_no = ''
				regno = ''
				reg_no = ''
				if 'catEntName' in company_text:
					ent_name = company_text['catEntName']
				if 'catRegNo' in company_text:
					reg_no = company_text['catRegNo']
				if len(reg_no) ==18:
					credit_no = reg_no
					regno = ''
				else:
					regno = reg_no
					credit_no = ''
				self.province = u'浙江省'
				sql_1 = "select * from Business_Abnormal where enterprisename='%s'" % ent_name
				res_1 =execute_query(sql_1)
				if len(res_1) == 0:
					sql = "insert into Business_Abnormal values('%s','%s','%s','%s',now())" % (ent_name, self.province, regno, credit_no)
					print sql
					excute_update(sql)
			# mysql.commit()
			print u'第%s页更新完成' % num
			num += 1
			with open(num_path, 'wb') as f:
				f.write(str(num))
				f.close()


if __name__ == '__main__':
    update_searcher = ZheJiangSearcher()
    update_searcher.update_proc()

