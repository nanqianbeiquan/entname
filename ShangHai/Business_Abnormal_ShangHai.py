# coding=utf-8

import PackageTool
from database import MSSQL
from TimeUtils import *
import json
from ba.Searcher import Searcher
from requests.exceptions import RequestException
from requests.exceptions import ReadTimeout
from bs4 import BeautifulSoup
import MySQLdb
import os
import sys
import random
import subprocess
import requests
import traceback
requests.packages.urllib3.disable_warnings()


mysql = MSSQL()


class HeNanSearcher(Searcher):
    def __init__(self):
        super(HeNanSearcher, self).__init__(use_proxy=True, lock_ip=False)
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
                        "Host": "www.sgs.gov.cn",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Connection": "keep-alive",
						"Referer": "https://www.sgs.gov.cn/notice/home",
						"Upgrade-Insecure-Requests": "1"
                        }

    def set_config(self):
		self.plugin_path = os.path.join(sys.path[0], '../ShangHai/ocr/type34.bat')
		self.add_proxy()

    def get_validate_image_save_path(self):
        return os.path.join(sys.path[0], '../ShangHai/ocr/' + str(random.random())[2:] + '.png')

    def get_validate_file_path(self):
        return os.path.join(sys.path[0], '../ShangHai/ocr/' + str(random.random())[2:] + '.txt')

    def recognize_yzm(self,validate_path,validate_result_path):
		self.plugin_path = os.path.join(sys.path[0], '../ShangHai/ocr/type34.bat')
		cmd = self.plugin_path + " " + validate_path+ " " + validate_result_path
        # print cmd
		p=subprocess.Popen(cmd.encode('gbk','ignore'), stdout=subprocess.PIPE)
		p.communicate()
		fo = open(validate_result_path,'r')
		answer=fo.readline().strip()
		fo.close()
		print 'answer: '+answer.decode('gbk', 'ignore')
		os.remove(validate_path)
		os.remove(validate_result_path)
		return answer.decode('gbk', 'ignore')

    def get_yzm(self):
        params = {'ra': '%.15f' % random.random(), 'preset:': ''}
        image_url = 'https://www.sgs.gov.cn/notice/captcha?preset=&ra=0.5626257367945652'
        r = self.get_request(image_url, params, verify=False)
        yzm_path = self.get_validate_image_save_path()
        with open(yzm_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
        yzm_file_path =self.get_validate_file_path()
        yzm = self.recognize_yzm(yzm_path,yzm_file_path)
        return yzm

    def update_proc(self):
		credit_no = ''
		regno = ''
		self.num_path = os.path.join(sys.path[0], '../ShangHai/num.txt')
		num_path = self.num_path
		url = "https://www.sgs.gov.cn/notice/search/ent_except_list"
		while True:
			with open(num_path, 'rb') as f:
				num = int(f.read())
				f.close()
			yzm = self.get_yzm()
			params = {"condition.pageNo": num, "captcha": yzm, "session.token": u'2851bffc-c01d-4f34-9f56-7cfc37e54f7a'}
			r = self.post_request(url=url, params=params, verify=False)
			r.encoding = 'utf-8'
			soup = BeautifulSoup(r.text,'lxml')
			body_text = soup.select('html > body > div > div > table > tr')[1:]
			# print body_text
			for company_text in body_text:
				ent_name = company_text.select('td')[0].text.strip()
				ent_name = ent_name.replace('\\','')
				reg_no = company_text.select('td')[1].text.strip()
				if len(reg_no) ==18:
					regno = ''
					credit_no = reg_no
				else:
					regno = reg_no
					credit_no = ''
				self.province = u'上海市'
				sql = "insert into Business_Abnormal values('%s','%s','%s','%s',now())" % (ent_name, self.province, regno, credit_no)
				print sql
				mysql.execute(sql)
			mysql.commit()
			print u'第%s页更新完成' % num
			num += 1
			with open(num_path, 'wb') as f:
				f.write(str(num))
				f.close()

    def post_request(self, url, params={}, data={}, verify=True, t=0, release_lock_id=False, timeout=None):
        """
        发送post请求,包含添加代理,锁定ip与重试机制
        :param url: 请求的url
        :param params: 请求参数
        :param data: 请求数据
        :param verify: 忽略ssl
        :param t: 重试次数
        :param release_lock_id: 是否需要释放锁定的ip资源
        :param timeout: 超时时间
        :return:
        """
        if not timeout:
            timeout = self.timeout
        try:
            if self.use_proxy:
                if not release_lock_id:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id)
                else:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.lock_id)
            r = self.session.post(url=url, headers=self.headers, params=params, data=data, verify=verify, timeout=timeout)
            # print r.text
            if r.status_code == 200:
                return r
            else:
				self.update_proc()
				print u'错误的响应代码 -> %d' % r.status_code
				if t == 15:
					raise RequestException()
				else:
					return self.post_request(url, params, data, verify, t + 1, release_lock_id, timeout)
            return r
        except (RequestException, ReadTimeout) as e:
            traceback.print_exc(e)
            if t == 15:
                raise e
            else:
                return self.post_request(url, params, data, verify, t+1, release_lock_id, timeout)

if __name__ == '__main__':
    update_searcher = HeNanSearcher()
    update_searcher.update_proc()

