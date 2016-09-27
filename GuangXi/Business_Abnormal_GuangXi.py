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


class HaiNanSearcher(Searcher):
    def __init__(self):
        super(HaiNanSearcher, self).__init__()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
                        "Host": "gxqyxygs.gov.cn",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Connection": "keep-alive",
						"Referer": "http://gxqyxygs.gov.cn/exceptionInfoSelect.jspx",
						"Upgrade-Insecure-Requests": "1"
                        }

    def set_config(self):
		self.add_proxy()

    def update_proc(self):
		credit_no = ''
		regno = ''
		self.num_path = os.path.join(sys.path[0], '../GuangXi/num.txt')
		num_path = self.num_path
		url = "http://gxqyxygs.gov.cn/exceptionInfoSelect.jspx"
		while True:
			with open(num_path, 'rb') as f:
				num = int(f.read())
				f.close()
			params = {"pageNo": num}
			r = self.post_request(url, params=params)
			r.encoding = 'utf-8'
			soup = BeautifulSoup(r.text,'lxml')
			body_text = soup.select('html > body > div > div > div > div')[2:-1]
			for company_text in body_text:
				ent_name = company_text.select('ul > li')[0].text.strip()
				ent_name = ent_name.replace('\\','')
				reg_no = company_text.select('ul > li')[1].text.strip()
				if len(reg_no) ==18:
					regno = ''
					credit_no = reg_no
				else:
					regno = reg_no
					credit_no = ''
				self.province = u'广西壮族自治区'
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
    update_searcher = HaiNanSearcher()
    update_searcher.update_proc()

