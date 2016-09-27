# coding=utf-8

import PackageTool
from database import MSSQL
from TimeUtils import *
import json
from Searcher import Searcher
from lxml import html
import sys
import os


mysql = MSSQL()


class HuBeiSearcher(Searcher):
    def __init__(self):
        super(HuBeiSearcher, self).__init__()
        self.credit_no = ""
        self.reg_no = ''
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
                        "Host": "xyjg.egs.gov.cn",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Connection": "keep-alive",
                        }

    def set_config(self):  # 设置代理
        self.add_proxy()

    def update_proc(self):  # 更新函数
        url = "http://xyjg.egs.gov.cn/ECPS_HB/exceptionInfoSelect.jspx"
        while True:
            self.credit_no = ""  # 信用代码
            self.reg_no = ''  # 注册号
            txt_path = os.path.join(sys.path[0], 'num.txt')
            with open(txt_path, 'rb') as f:
                num = int(f.read())
                f.close()
            if num == 87417:
                break
            params = {"gjz": '', "pageNo": num}
            r = self.post_request(url, data=params)
            r.encoding = 'utf-8'
            tree = html.fromstring(r.text)
            result_list = tree.xpath(".//div/div[2]/div/ul")[1:]
            if not result_list:
                print u'更新完成'
                break
            for result in result_list:
                name = result.xpath("li/a")[0].text.strip()
                ent_no = result.xpath("li[2]")[0].text.strip()
                if ent_no:
                    if len(ent_no) == 18:
                        self.credit_no = ent_no
                    else:
                        self.reg_no = ent_no
                    province = u'湖北省'
                sql = "insert into Business_Abnormal values('%s','%s','%s','%s',now())" % (name, province, self.reg_no, self.credit_no)
                mysql.execute(sql)
            mysql.commit()
            print u'第%s页更新完成' % num
            num += 1
            with open(txt_path, 'wb') as f:
                f.write(str(num))
                f.close()


if __name__ == '__main__':
    update_searcher = HuBeiSearcher()
    update_searcher.update_proc()

# with open("num.txt", 'rb') as f:
#     num = f.read()
#     f.close()
#     print num
