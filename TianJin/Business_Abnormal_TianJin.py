# coding=utf-8

import PackageTool
from database import MSSQL
from TimeUtils import *
import json
from Searcher import Searcher
from lxml import html

mysql = MSSQL()


class JiangSuSearcher(Searcher):
    def __init__(self):
        super(JiangSuSearcher, self).__init__()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
                        "Host": "tjcredit.gov.cn",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Connection": "keep-alive",
                        }

    def set_config(self):
        self.add_proxy()

    def update_proc(self):
        url = "http://tjcredit.gov.cn/platform/saic/excsearch.ftl"
        while True:
            with open("num.txt", 'rb') as f:
                num = int(f.read())
                f.close()
            params = {"searchContent": '', "page": num}
            r = self.post_request(url, data=params)
            r.encoding = 'utf-8'
            tree = html.fromstring(r.text)
            name_list = tree.xpath(".//ul/li[1]/a")
            for name in name_list:
                name = name.text.strip()
                province = u'天津市'
                if name != u'无':
                    sql = "insert into Business_Abnormal(enterprisename,province,update_time) values('%s','%s',now())" % (name, province)
                    mysql.execute(sql)
            mysql.commit()
            print u'第%s页更新完成' % num
            num += 1
            with open("num.txt", 'wb') as f:
                f.write(str(num))
                f.close()


if __name__ == '__main__':
    update_searcher = JiangSuSearcher()
    update_searcher.update_proc()

# with open("num.txt", 'rb') as f:
#     num = f.read()
#     f.close()
#     print num
