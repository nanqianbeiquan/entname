# coding=utf-8
import re
import os
import subprocess
import sys
import MSSQL
import json
import datetime
from requests.exceptions import RequestException
from requests.exceptions import ReadTimeout
from ProxyConf import ProxyConf, key3 as app_key
import requests
import urllib
from uuid import uuid1
import time
import random
import traceback


class Searcher(object):

    pattern = re.compile("\s")
    cur_mc = ''  # 当前查询公司名称
    cur_zch = ''  # 当前查询公司注册号
    json_result = {}  # json输出结果
    plugin_path = None  # 验证码插件路径
    kafka = None  # kafka客户端
    save_tag_a = True  # 是否需要存储tag_a
    today = None  # 当天
    session = None  # 提交请求所用session
    province = None  # 省份
    topic = None  # 获取公司名称的队列
    group = None  # 获取公司名称的组
    use_proxy = False  # 是否需要用代理

    lock_ip = False  # 使用代理时是否需要锁定ip
    lock_id = 0  # ip锁定标识
    proxy_config = None  # 代理浏览器头生成器
    uuid = str(uuid1())  # 进程唯一性标识,用于ip锁定和解锁
    last_lock_time = -1
    timeout = 15  # request最大等待时间

    def __init__(self, use_proxy=False, lock_ip=False):
        # self.kafka.init_producer()
        self.session = requests.session()
        self.use_proxy = use_proxy
        self.lock_ip = lock_ip
        if self.use_proxy:
            self.proxy_config = ProxyConf(app_key)
            self.session.proxies = self.proxy_config.get_proxy()

    def add_proxy(self, key):
        if self.use_proxy:
            self.proxy_config = ProxyConf(key)
            self.session.proxies = self.proxy_config.get_proxy()

    def set_request_timeout(self, t):
        self.timeout = t

    def set_config(self):
        """
        设置参数(self.plugin_path)
        :return:
        """
        pass

    def submit_search_request(self, keyword, account_id='null', task_id='null'):
        """
        提交查询请求
        :param keyword: 查询关键词(公司名称或者注册号/信用代码)
        :param account_id: 在线更新,kafka所需参数
        :param task_id: 在线更新kafka所需参数
        :return:
        """
        # 锁定ip时间超过30秒,重新获取lock_id

        if self.use_proxy and self.lock_ip:
            lock_time = time.time()
            if lock_time - self.last_lock_time >= 30:
                self.lock_id = self.proxy_config.get_lock_id(self.uuid)
            else:
                pass
                # self.update_lock_time()  # 重置锁定时间
            self.last_lock_time = lock_time

        self.cur_mc = ''  # 当前查询公司名称
        self.cur_zch = ''  # 当前查询公司注册号
        self.today = str(datetime.date.today()).replace('-', '')
        self.json_result.clear()
        self.save_tag_a = True
        keyword = keyword.replace('(', u'`（').replace(')', u'）')  # 公司名称括号统一转成全角
        print u'keyword: %s' % keyword
        tag_a = self.get_tag_a_from_db(keyword)
        if not tag_a:
            tag_a = self.get_tag_a_from_page(keyword)
        if tag_a:
            args = self.get_search_args(tag_a, keyword)
            if len(args) > 0:
                if self.save_tag_a:  # 查询结果与所输入公司名称一致时,将其写入数据库
                    self.save_tag_a_to_db(tag_a)
                print u'解析详情信息'
                self.parse_detail(args)
                self.json_result['inputCompanyName'] = keyword
                self.json_result['accountId'] = account_id
                self.json_result['taskId'] = task_id
                print u'消息写入kafka'
                self.kafka.send(json.dumps(self.json_result, ensure_ascii=False))
                # print json.dumps(self.json_result, ensure_ascii=False)
            else:
                print u'查询结果不一致'
                save_dead_company(keyword)
        else:
            print u'查询无结果'
            save_dead_company(keyword)

    def get_search_args(self, tag_a, keyword):
        """
        :param tag_a: tag_a
        :param keyword: 查询关键词
        根据tag_a解析查询所需参数, 如果查询结果和输入公司名不匹配返回空列表
        :rtype: list
        :return: 查询所需参数
        """
        return []

    def get_tag_a_from_db(self, keyword):
        """
        从数据库中查询tag_a, 如果数据库中存在tag_a,直接返回,否则需要提交验证码进行查询
        :param keyword: 查询关键词
        :rtype: str
        :return: 查询详情所需的tag_a
        """
        sql_1 = "select * from GsSrc.dbo.tag_a where mc='%s'" % keyword
        res_1 = MSSQL.execute_query(sql_1)
        if len(res_1) > 0:
            self.save_tag_a = False
            tag_a = res_1[0][1]
            return tag_a
        else:
            return None

    def get_tag_a_from_page(self, keyword):
        """
        从页面上通过提交验证码获取tag_a
        :param keyword: 查询关键词
        :rtype: str
        :return: tag_a
        """
        pass

    def save_tag_a_to_db(self, tag_a):
        """
        将通过提交验证码获取到的tag_a存储到数据库中
        :param tag_a: 查询关键词
        :return:
        """
        sql = "insert into GsSrc.dbo.tag_a values ('%s','%s',getdate())" % (self.cur_mc, tag_a)
        MSSQL.execute_update(sql)

    def get_yzm(self):
        """
        获取验证码
        :rtype: str
        :return: 验证码识别结果
        """
        print u'下载验证码...'
        yzm_path = self.download_yzm()
        print u'识别验证码...'
        yzm = self.recognize_yzm(yzm_path)
        os.remove(yzm_path)
        return yzm

    def get_yzm_path(self):
        return os.path.join(sys.path[0], '../temp/' + str(random.random())[2:] + '.jpg')

    def download_yzm(self):
        """
        下载验证码图片
        :rtype str
        :return 验证码保存路径
        """
        return ""

    def recognize_yzm(self, yzm_path):
        """
        识别验证码
        :param yzm_path: 验证码保存路径
        :return: 验证码识别结果
        """
        cmd = self.plugin_path + " " + yzm_path
        print cmd
        process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
        process_out = process.stdout.read()
        answer = process_out.split('\r\n')[6].strip()
        # print 'answer: ' + answer
        return answer.decode('gbk', 'ignore')

    def parse_detail(self, kwargs):
        """
        解析公司详情信息
        :param kwargs:
        :return:
        """
        # print u'解析基本信息...'
        self.get_ji_ben(*kwargs)
        # print u'解析股东信息...'
        self.get_gu_dong(*kwargs)
        # print u'解析变更信息...'
        self.get_bian_geng(*kwargs)
        # print u'解析主要人员信息...'
        self.get_zhu_yao_ren_yuan(*kwargs)
        # print u'解析分支机构信息...'
        self.get_fen_zhi_ji_gou(*kwargs)
        # print u'解析清算信息...'
        self.get_qing_suan(*kwargs)
        # print u'解析动产抵押信息...'
        self.get_dong_chan_di_ya(*kwargs)
        # print u'解析股权出质信息...'
        self.get_gu_quan_chu_zhi(*kwargs)
        # print u'解析行政处罚信息...'
        self.get_xing_zheng_chu_fa(*kwargs)
        # print u'解析经营异常信息...'
        self.get_jing_ying_yi_chang(*kwargs)
        # print u'解析严重违法信息...'
        self.get_yan_zhong_wei_fa(*kwargs)
        # print u'解析抽查检查信息...'
        self.get_chou_cha_jian_cha(*kwargs)
        # self.get_nian_bao_link(*kwargs)

    def get_ji_ben(self, **kwargs):
        """
        获取基本信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_gu_dong(self, **kwargs):
        """
        获取股东信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_bian_geng(self, **kwargs):
        """
        获取变更信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_zhu_yao_ren_yuan(self, **kwargs):
        """
        获取主要人员信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_fen_zhi_ji_gou(self, **kwargs):
        """
        获取分支机构信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_qing_suan(self, **kwargs):
        """
        获取清算信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_dong_chan_di_ya(self, **kwargs):
        """
        获取动产抵押信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_gu_quan_chu_zhi(self, **kwargs):
        """
        获取股权出质信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_xing_zheng_chu_fa(self, **kwargs):
        """
        获取行政处罚信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_jing_ying_yi_chang(self, **kwargs):
        """
        获取经营异常信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_yan_zhong_wei_fa(self, **kwargs):
        """
        获取严重违法信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_chou_cha_jian_cha(self, **kwargs):
        """
        获取抽查检查信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_nian_bao_link(self, **kwargs):
        """
        获取年报信息
        :param kwargs: 查询参数
        :return:
        """
        pass

    def get_request(self, url, params={}, data={}, verify=True, t=0, release_lock_id=False, timeout=None):
        """
        发送get请求,包含添加代理,锁定ip与重试机制
        :param url: 请求的url
        :param params: 请求参数
        :param data: 请求数据
        :param verify: 忽略ssl
        :param t: 重试次数
        :param release_lock_id: 是否需要释放锁定的ip资源
        :param timeout: 超时时间
        """
        if not timeout:
            timeout = self.timeout
        try:
            if self.use_proxy:
                if not release_lock_id:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id)
                else:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=self.lock_id, release_id=self.lock_id)
            r = self.session.get(url=url, headers=self.headers, params=params, data=data, verify=verify, timeout=timeout)
            if r.status_code == 200:
                return r
            else:
                print u'错误的响应代码 -> %d' % r.status_code
                if t == 15:
                    raise RequestException()
                else:
                    return self.get_request(url, params, data, verify, t + 1, release_lock_id, timeout)
            return r
        except (RequestException, ReadTimeout) as e:
            traceback.print_exc(e)
            if t == 15:
                raise e
            else:
                return self.get_request(url, params, data, verify, t+1, release_lock_id, timeout)

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

    def get_request_302(self, url, params={}, lock_ip=True, t=0):
        """
        手动处理包含302的请求
        :param url:
        :param params:
        :param lock_ip:
        :param t:
        :return:
        """
        try:
            lock_id = 0
            if self.use_proxy and lock_ip:
                lock_id = self.proxy_config.get_lock_id()
            for i in range(10):
                if self.use_proxy:
                    self.headers['Proxy-Authorization'] = self.proxy_config.get_auth_header(lock_id=lock_id)
                r = self.session.get(url=url, headers=self.headers, params=params, allow_redirects=False)
                if r.status_code == 302:
                    protocal, addr = urllib.splittype(url)
                    url = protocal + '://' + urllib.splithost(addr)[0] + r.headers['Location']
                else:
                    return r
        except (RequestException, ReadTimeout) as e:
            if t == 5:
                raise e
            else:
                return self.get_request_302(url, params, lock_ip, t + 1)

    def update_lock_time(self):
        """
        更新ip锁定时间
        :return:
        """
        sql = "update GsSrc.dbo.lock_id_status set last_lock_time=getdate() where app_key='%s' and lock_id=%d" \
              % (self.proxy_config.app_key, self.lock_id)
        MSSQL.execute_update(sql)


def save_dead_company(company_name):
    """
    将查询无结果的公司名保存, 下次不做更新
    :param company_name:
    :return:
    """
    sql_1 = "select * from GsSrc.dbo.dead_company where company_name='%s'" % company_name
    # print sql_1
    res_1 = MSSQL.execute_query(sql_1)
    if len(res_1) == 0:
        sql_2 = "insert into GsSrc.dbo.dead_company values('%s',getdate())" % company_name
        # print sql_2
        MSSQL.execute_update(sql_2)


def get_args():
    args = dict()
    for arg in sys.argv:
        kv = arg.split('=')
        if kv[0] == 'companyName':
            args['companyName'] = kv[1].decode(sys.stdin.encoding, 'ignore')
        elif kv[0] == 'taskId':
            args['taskId'] = kv[1].decode(sys.stdin.encoding, 'ignore')
        elif kv[0] == 'accountId':
            args['accountId'] = kv[1].decode(sys.stdin.encoding, 'ignore')
    return args


def delete_tag_a_from_db(keyword):
    """
    从数据库中删除现存的tag_a
    :param keyword: 查询关键词
    """
    sql_1 = "delete from GsSrc.dbo.tag_a where mc='%s'" % keyword
    MSSQL.execute_update(sql_1)
