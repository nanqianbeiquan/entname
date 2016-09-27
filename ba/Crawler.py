# coding=utf-8

import PackageTool
from KafkaAPI import KafkaAPI
from ProxyConf import key2 as app_key

from liao_ning.LiaoNingSearcher import LiaoNingSearcher
from shanghai.ShangHaiSearcher import ShangHaiSearcher
from ZheJiang.ZheJiangSearcher import ZheJiangSearcher
from bei_jing.BeiJing import BeiJing
from guangdong.Guangdong import Guangdong
from jiang_su.JiangSuSearcher import JiangSuSearcher
from he_nan.HeNanSearcher import HeNanSearcher
from fu_jian.FuJianSearcher import FuJianSearcher
from hu_bei.HuBei import HuBeiSearcher
from chong_qing.ChongQingSearcher import ChongQingSearcher
from jiang_xi.JiangXiSearcher import JiangXiSearcher
from hu_nan.HuNan import HuNanSearcher
from tian_jin.TianJin import TianJinSearcher
from he_bei.HeBei import HeBei
from nei_meng_gu.NeiMengGuSearcher import NeiMengGuSearcher
from ji_lin.JiLinSearcher import JiLinSearcher
from guang_xi.GuangXiSearcher import GuangXiSearcher
from hai_nan.HaiNanSearcher import HaiNanSearcher
from sshan_xi.SShanXiSearcher import SShanXiSearcher
from gan_su.GanSu import GanSuSearcher
from ning_xia.NingXia import NingXia
from xin_jiang.XinJiang import XinJiang
from shan_dong.ShanDongSearcher import ShanDongSearcher
from gui_zhou.GuiZhouSearcher import GuiZhouSearcher
from hei_longjiang.HeiLongJiang import HeiLongJiang
from an_hui.AnHui import AnHui
from shanm_xi.ShanmXi import ShanmXi
from xi_zang.XiZang import XiZang
from qing_hai.QingHai import QingHai
from si_chuan.SiChuan import SiChuanSearcher
from yun_nan.YunNanSearcher import YunNanSearcher
from zong_ju.ZongJu import ZongJu

import sys
import json
reload(sys)
sys.setdefaultencoding('utf8')


class GsCrawler(object):

    crawler_class_dict = {
        u'北京市': BeiJing,
        u'辽宁省': LiaoNingSearcher,
        u'上海市': ShangHaiSearcher,
        u'浙江省': ZheJiangSearcher,
        u'广东省': Guangdong,
        u'河南省': HeNanSearcher,
        u'福建省': FuJianSearcher,
        u'江苏省': JiangSuSearcher,
        u'宁夏回族自治区': NingXia,
        u'湖北省': HuBeiSearcher,
        u'海南省': HaiNanSearcher,
        u'重庆市': ChongQingSearcher,
        u'江西省': JiangXiSearcher,
        u'贵州省': GuiZhouSearcher,
        u'四川省': SiChuanSearcher,
        u'天津市': TianJinSearcher,
        u'安徽省': AnHui,
        u'湖南省': HuNanSearcher,
        u'河北省': HeBei,
        u'陕西省': SShanXiSearcher,
        u'山西省': ShanmXi,
        u'山东省': ShanDongSearcher,
        u'黑龙江省': HeiLongJiang,
        u'吉林省': JiLinSearcher,
        u'内蒙古自治区': NeiMengGuSearcher,
        u'广西壮族自治区': GuangXiSearcher,
        u'海南省': HaiNanSearcher,
        u'贵州省': GuiZhouSearcher,
        u'云南省': YunNanSearcher,
        u'西藏自治区': XiZang,
        u'青海省': QingHai,
        u'新疆维吾尔自治区': XinJiang,
        u'甘肃省': GanSuSearcher,
        u'工商总局': ZongJu
    }

    crawler_dict = {}
    app_key = app_key

    def __init__(self):
        pass

    def set_app_key(self, key=app_key):
        self.app_key = key

    def crawl(self, company_name, province, task_id='null', account_id='null', topic='GSRealTime'):
        if province not in self.crawler_dict:
            if province in self.crawler_class_dict:
                self.crawler_dict[province] = self.crawler_class_dict[province]()
                print app_key
                self.crawler_dict[province].add_proxy(self.app_key)
                self.crawler_dict[province].kafka = KafkaAPI(topic)
                self.crawler_dict[province].kafka.init_producer()
                self.crawler_dict[province].group = 'Crawler'

            else:
                raise Exception(province+u'爬虫未上线!')
        # print type(company_name)
        self.crawler_dict[province].submit_search_request(keyword=company_name, account_id=account_id, task_id=task_id)


def get_args():
    args = dict()
    for arg in sys.argv:
        kv = arg.split('=')
        if len(kv) == 2:
            k = kv[0]
            if k != 'topic':
                v = kv[1].decode('gbk', 'ignore')
            else:
                v = kv[1]
            args[k] = v
        # if kv[0] == 'companyName':
        #     args['companyName'] = kv[1].decode('gbk', 'ignore')
        # elif kv[0] == 'taskId':
        #     args['taskId'] = kv[1].decode('gbk', 'ignore')
        # elif kv[0] == 'accountId':
        #     args['accountId'] = kv[1].decode('gbk', 'ignore')
        # elif kv[0] == 'province':
        #     args['province'] = kv[1].decode('gbk', 'ignore')
        # elif kv[0] == 'topic':
        #     args['topic'] = kv[1]
    return args

if __name__ == '__main__':
    args_dict = get_args()
    if len(args_dict) < 5:
        args_dict = {'companyName': u'光大资本投资有限公司', 'province': u'上海市',
                     'taskId': '123', 'accountId': '456',
                     'topic': 'GSRealTime'}
    print json.dumps(args_dict, ensure_ascii=False)
    crawler = GsCrawler()
    crawler.crawl(company_name=args_dict['companyName'], province=args_dict['province'],
                  task_id=args_dict['taskId'], account_id=args_dict['accountId'], topic=args_dict['topic'])

