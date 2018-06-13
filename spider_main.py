#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

# URL管理器
"""
添加新的URL到待爬取集合中
判断待添加URL是否在容器中
获取待爬取URL
判断是否还有待爬取URL
将URL从待爬取移动到已爬取
"""

# 网页下载器
import urllib2

"""
urllib2
requests
"""

# 网页解析器
"""
正则表达式
html.parser
BeautifulSoup
lxml
"""
import httplib
import url_manager, html_downloader, html_outputer, html_parser
import os
import sys
import codecs
import datetime
import logging
import threadpool
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool


class SpiderMain(object):
    def __init__(self):
        # self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()

    def craw(self, root_url, full_path, name):
        '''
        :param root_url: 搜狗微信的搜索url
        :param full_path: 存储的文件目录
        :param name: 公众号的名称
        :return:
        '''
        new_url = root_url
        # html = None
        # try:
        #     html = self.downloader.download_list_ph(new_url, name)
        # except httplib.IncompleteRead as e:
        #     with open(r'list_error.txt', 'a') as f:
        #         f.write(name.encode('utf-8'))
        #         f.write('\n')
        # if html == None:
        #     return
        # wechat_url, html_cont = html
        # acticle_links = self.parser.parse_list(wechat_url, html_cont)
        # if acticle_links == None:
        #     return
        html = None
        html_list = None
        try:
            html = self.downloader.download_list_ph(new_url, name)
        except httplib.IncompleteRead as e:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
        if html is None:
            return
        link, page_source = html
        # data = self.parser.parse_wechat(page_source)
        # self.outputer.wechat_info(data)
        try:
            html_list = self.downloader.download_list_ph_2(name, link)
        except httplib.IncompleteRead as e:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')

        if html_list is None:
            return

        acticle_links = self.parser.parse_list(link, html_list)
        if acticle_links is None:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
            return

        for link in acticle_links:
            html = self.downloader.download_articles_ph(link)
            data = self.parser.parse_article(html)  # 解析出文本
            if data == None:
                continue
            (title, wname, date, content, readNum, praise_num, discuss_content, discuss_praise) = data
            self.outputer.output_mongodb(name, data)
    f = open('category1.csv', 'a')
    def task(self,link):
        data = None
        while data is None:
            html = self.downloader.download_articles_ph(link)
            data = self.parser.parse_article(html)
            self.f.write(data[1] + '#' + data[0] + '#' + data[2] + '#' + data[3])
            self.f.write('\n')
            self.f.flush()

    def craw4key(self, key):
        f = open('category1.csv', 'a')
        cookie = self.downloader.get_cookies()
        for i in range(11, 20):
            print('the page is %d' % i)
            root_url = u"http://weixin.sogou.com/weixin?type=2&page=%d&ie=utf8&s_from=hotnews&query=%s" % (i, key)
            html_list = self.downloader.download_list4key(root_url, cookie)
            # pool = ThreadPool(6)
            # pool.map(self.downloader.download_articles_ph, html_list)
            # pool.close()
            # pool.join()
            for link in html_list:
                data = None
                while data is None:
                    html = self.downloader.download_articles_ph(link)
                    data = self.parser.parse_article(html)  # 解析出文本
                f.write(data[1] + '#' + data[0] + '#' + data[2] + '#' + data[3])
                f.write('\n')
                f.flush()
        f.close()

    def schedule(self, name):
        if name == '':
            return 0
        root_url = "http://weixin.sogou.com/weixin?type=%d&query=%s" % (1, name)
        full_path = None
        # full_path = new_path(name)  # 存储目录
        # type:表示搜索类型 querystring:表示公众号 i:表示网页页数1
        # oneday = datetime.timedelta(days=1)
        # today = str(datetime.date.today())
        # file_name = full_path+r'\%s.csv' % today
        # if os.path.exists(file_name):
        #     return 0
        try:
            self.craw(root_url, full_path, name)
        except urllib2.URLError as e:
            print(datetime.datetime.now())
            print(e)
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')

        return 1

    def list_multiprocess(self, filename):
        name_list = []
        with open(filename) as fout:
            for name in fout:
                if name[:3] == codecs.BOM_UTF8:
                    name = name[3:]
                named = name.strip('.\n').decode('utf-8')
                # print named
                name_list.append(named)

        pool = ThreadPool(6)
        pool.map(self.schedule, name_list)
        pool.close()
        pool.join()
        self.error_handle()

    def single_job(self, filename):
        with open(filename) as fout:
            for name in fout:
                if name[:3] == codecs.BOM_UTF8:
                    name = name[3:]
                named = name.strip('.\n').decode('utf-8')
                print named
                self.schedule(named)
        self.error_handle()
        os.remove('list_error.txt')

    # 多线程的格式预处理
    def list_handle(self, filename):
        name_list = []
        with open(filename) as fout:
            for name in fout:
                if name[:3] == codecs.BOM_UTF8:
                    name = name[3:]
                named = name.strip('.\n').decode('utf-8')
                print named
                name_list.append(named)
        pool = threadpool.ThreadPool(4)
        requests = threadpool.makeRequests(self.schedule, name_list)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        print('destory all threads')
        pool.dismissWorkers(4, True)

    def error_handle(self):
        number = 0
        while os.path.exists('list_error.txt'):
            number = number + 1
            print ('the number for handling is %d' % number)
            print('start list_error download')
            print(datetime.datetime.now())
            with open('list_error.txt', ) as f:
                names = f.readlines()
            for i, name in enumerate(names):
                names[i] = name.strip('\n')
            os.remove('list_error.txt')
            print(names)
            pool1 = ThreadPool(3)
            try:
                pool1.map(self.schedule, names)
                pool1.close()
                pool1.join()
            except:
                pass
            print(datetime.datetime.now())


path = u'd:\\wechat_data1'


def mk_dir(full_path):
    full_path = full_path.strip()
    full_path = full_path.rstrip("\\")
    # 判断路径是否存在
    is_exists = os.path.exists(full_path)
    if not is_exists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(full_path)
        return True
    else:
        pass
        # 如果目录存在则不创建，并提示目录已存在


def new_path(name):
    full_path = path + r'\%s' % name
    mk_dir(full_path)
    return full_path


def job_period():
    # ip_pool.ip_collect() # 采集代理ip
    obj_spider = SpiderMain()
    # obj_spider.single_job('D:\\WechatList.txt')
    obj_spider.list_multiprocess('D:\\WechatList.txt')

    os.remove('wechat.txt')


if __name__ == "__main__":
    # logging.basicConfig(filename='log.txt')
    # sched = BlockingScheduler()
    # sched.add_job(job_period, 'cron', start_date='2017-01-01', hour=1, minute=0, second=0, end_date='2017-12-30')
    # a = sched.get_jobs()
    # print(a)
    # sched.start()

    # job_period()
    spider = SpiderMain()
    # spider.single_job('D:\\WechatList.txt')
    spider.craw4key(u'中兴跳楼')
