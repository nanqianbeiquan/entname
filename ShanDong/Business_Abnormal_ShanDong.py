# coding=utf-8

import PackageTool
from database import MSSQL
from TimeUtils import *
import json
from bs4 import BeautifulSoup
from Searcher import Searcher


mysql = MSSQL()


class ShanDongSearcher(Searcher):
    def __init__(self):
        super(ShanDongSearcher, self).__init__()
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Connection': 'keep-alive',
                        'Host': '218.57.139.24',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'}
        url1 = 'http://218.57.139.24/'
        r = self.get_request(url1)
        bs1 = BeautifulSoup(r.text, 'lxml')
        token = bs1.select('meta')[3].attrs['content']
        self.token = token

    def set_config(self):
        self.add_proxy()

    def update_proc(self):
        credit_no = ''
        regno = ''
        url = "http://218.57.139.24/pub/jyyc"
        self.headers['X-CSRF-TOKEN'] = self.token
        print 'self.token', self.token
        while True:
            with open("num.txt", 'rb') as f:
                num = int(f.read())
                f.close()
            params = {"page": num}
            r = self.post_request(url=url, data=params)
            r.encoding = 'utf-8'
            json_dict = json.loads(r.text)
            values = json_dict
            if not values:
                print u'数据更新结束'
                break
            for value in values:
                ent_name = value["entname"]
                ent_no = value["regno"]
                if ent_no:
                    if len(ent_no) == 18:
                        credit_no = ent_no
                        reg_no = ''
                    else:
                        reg_no = ent_no
                        credit_no = ''
                    province = u'山东省'
                    # sql = "insert into Business_Abnormal values('%s','%s','%s','%s',now())" % (ent_name, province, reg_no, credit_no)
                    # mysql.execute(sql)
                    print num, ent_name, ent_no
            mysql.commit()
            print u'第%s页更新完成' % num
            num += 1
            with open("num.txt", 'wb') as f:
                f.write(str(num))
                f.close()


if __name__ == '__main__':
    update_searcher = ShanDongSearcher()
    update_searcher.update_proc()


