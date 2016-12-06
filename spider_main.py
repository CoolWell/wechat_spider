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
        # self.urls.add_new_url(root_url)
        # while self.urls.has_new_url():
        # new_url = self.urls.get_new_url()#从url列表中取出url
        new_url = root_url
        html = None
        try:
            html = self.downloader.download_list_ph(new_url, name)
        except httplib.IncompleteRead as e:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
        if html == None:
            return
        wechat_url, html_cont = html
        acticle_links = self.parser.parse_list(wechat_url, html_cont)
        if acticle_links == None:
            return

        for link in acticle_links:
            html = self.downloader.download_articles_ph(link)
            data = self.parser.parse_article(html)#解析出文本
            if data == None:
                continue
            (title, wname, date, content, readNum, praise_num, discuss_content, discuss_praise) = data
            # self.urls.add_new_urls(new_urls)
            # self.outputer.collect_data(data)
            self.outputer.output_mongodb(name, data)
            # self.outputer.output_file(full_path, data)

    def schedule(self, name):
        if name == '':
            return 0
        full_path = new_path(name)
        # type:表示搜索类型 querystring:表示公众号 i:表示网页页数1
        root_url = "http://weixin.sogou.com/weixin?type=%d&query=%s" % (1, name)
        oneday = datetime.timedelta(days=1)
        today = str(datetime.date.today())
        file_name = full_path+r'\%s.csv' % today
        if os.path.exists(file_name):
            return 0
        self.craw(root_url, full_path, name)
        return 1

    def list_multiprocess(self, filename):
        name_list = []
        with open(filename) as fout:
            for name in fout:
                if name[:3] == codecs.BOM_UTF8:
                    name = name[3:]
                named = name.strip('.\n').decode('utf-8')
                print named
                name_list.append(named)

        pool = ThreadPool(4)
        # results = \
        pool.map(self.schedule, name_list)
        pool.close()
        pool.join()
        # print(results)
        number = 0
        while os.path.exists('list_error.txt'):
            number = number+1
            print ('the number for handling is %d' % number)
            print('start list_error download')
            print(datetime.datetime.now())
            with open('list_error.txt',) as f:
                names = f.readlines()
            for i, name in enumerate(names):
                names[i] = name.strip('\n')
            os.remove('list_error.txt')
            print(names)
            pool1 = ThreadPool(8)
            # results =
            pool1.map(self.schedule, names)
            pool1.close()
            pool1.join()
            # print(results)
            print(datetime.datetime.now())


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
        if os.path.exists('list_error.txt'):
            print('start list_error download')
            print(datetime.datetime.now())
            with open('list_error.txt') as fout:
                for name in fout:
                    if name[:3] == codecs.BOM_UTF8:
                        name = name[3:]
                    named = name.strip('.\n').decode('utf-8')
                    print(named)
                    self.schedule(named)
            print(datetime.datetime.now())
            print('all down')


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
    # ip_pool.ip_collect()
    obj_spider = SpiderMain()
    obj_spider.list_multiprocess('D:\\WechatList.txt')
    # obj_spider.error_handle()
    # os.remove('list_error.txt')


if __name__ == "__main__":
    file = open('log.txt', 'a')
    sys.stdout = file
    # logging.basicConfig()
    # sched = BlockingScheduler()
    # sched.add_job(job_period, 'cron', start_date='2016-10-01', hour=11, minute=8, second=1, end_date='2016-12-30')
    # a = sched.get_jobs()
    # print(a)
    # sched.start()

    job_period()
    file.close()

