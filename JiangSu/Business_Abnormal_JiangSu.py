# coding=utf-8

import PackageTool
from database import MSSQL
from TimeUtils import *
import json
from Searcher import Searcher


mysql = MSSQL()


class JiangSuSearcher(Searcher):
    def __init__(self):
        super(JiangSuSearcher, self).__init__()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
                        "Host": "www.jsgsj.gov.cn:58888",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Connection": "keep-alive",
                        }

    def set_config(self):
        self.add_proxy()

    def update_proc(self):
        url = "http://www.jsgsj.gov.cn:58888/province/NoticeServlet.json?QueryExceptionDirectory=true"
        while True:
            with open("num.txt", 'rb') as f:
                num = int(f.read())
                f.close()
            params = {"corpName": '', "pageNo": num, "pageSize": 10, "showRecordLine":1, "tmp":get_cur_time_jiangsu()[:-6]}
            r = self.post_request(url, data=params)
            r.encoding = 'utf-8'
            json_dict = json.loads(r.text)
            values = json_dict["items"]
            if not values:
                print u'数据更新结束'
                break
            for value in values:
                ent_name = value["C1"]
                ent_no = value["C2"]
                if ent_no:
                    if len(ent_no) == 18:
                        credit_no = ent_no
                        reg_no = ''
                    else:
                        reg_no = ent_no
                        credit_no = ''
                    province = u'江苏省'
                    sql = "insert into Business_Abnormal values('%s','%s','%s','%s',now())" % (ent_name, province, reg_no, credit_no)
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
