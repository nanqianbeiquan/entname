# coding=utf-8

import requests
from requests.exceptions import RequestException, ReadTimeout
import time
from ProxyConf import ProxyConf, key1 as app_key
import traceback


class Searcher(object):

    def __init__(self, use_proxy=False, lock_ip=False):
        self.use_proxy = False
        self.session = requests.session()
        self.proxy_config = None
        self.headers = None
        self.timeout = 15
        self.add_proxy(app_key)
        self.use_proxy = use_proxy
        self.lock_ip = lock_ip
        if self.use_proxy:
            self.proxy_config = ProxyConf(app_key)
            self.session.proxies = self.proxy_config.get_proxy()

    def add_proxy(self, key):
        if self.use_proxy:
            self.proxy_config = ProxyConf(key)
            self.session.proxies = self.proxy_config.get_proxy()

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
