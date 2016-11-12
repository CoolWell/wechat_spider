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
from spider import url_manager, html_downloader, html_outputer, html_parser
import os
import codecs
import datetime
import logging
import threadpool
from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing.dummy import Pool as ThreadPool


class SpiderMain(object):

    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()

    def craw(self, root_url, full_path, name):
        self.urls.add_new_url(root_url)
        while self.urls.has_new_url():
                new_url = self.urls.get_new_url()#从url列表中取出url
                html = None
                try:
                    html = self.downloader.download_list_ph(new_url, name)
                except httplib.IncompleteRead as e:
                    with open(r'list_error.txt', 'a') as f:
                        f.write(name.encode('utf-8'))
                        f.write('\n')
                if html == None:
                    break
                wechat_url, html_cont = html
                acticle_links = self.parser.parse_list(wechat_url, html_cont)
                if acticle_links == None:
                    break

                for link in acticle_links:
                    html = self.downloader.download_articles_ph(link)
                    data = self.parser.parse_article(html)#解析出文本
                    if data == None:
                        continue
                    (title, date, content, readNum, praise_num, discuss_content, discuss_praise) = data
                    # self.urls.add_new_urls(new_urls)
                    # self.outputer.collect_data(data)
                    self.outputer.output_file(full_path, data)

obj_spider= SpiderMain()
path = u'd:\\wechat_data1'

def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # print path.encode('gbk') + ' 创建成功'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        pass
        # 如果目录存在则不创建，并提示目录已存在
        # print path.encode('gbk') + ' 目录已存在'


def new_path(path, name):

    full_path = path + r'\%s' % name
    mkdir(full_path)
    return full_path


def schedule(name):

    full_path = new_path(path, name)
    # type:表示搜索类型 querystring:表示公众号 i:表示网页页数1
    root_url = "http://weixin.sogou.com/weixin?type=%d&query=%s" % (1, name)
    oneday = datetime.timedelta(days=1)
    today = str(datetime.date.today())
    file_name = full_path+r'\%s.csv' % today
    if os.path.exists(file_name):
        return
    obj_spider.craw(root_url, full_path, name)
    return 1

def process(name):
    full_path = new_path(path, name)
    root_url = "http://weixin.sogou.com/weixin?type=%d&query=%s" % (1, name)
    oneday = datetime.timedelta(days=1)
    today = str(datetime.date.today())
    file_name = full_path+r'\%s.csv' % today
    if os.path.exists(file_name):
        return
    obj_spider.craw(root_url, full_path, name)
    return 1

def single_job(filename, path):
    obj_spider = SpiderMain()
    with open(filename) as fout:
        for name in fout:
            if name[:3] == codecs.BOM_UTF8:
                name = name[3:]
            named = name.strip('.\n').decode('utf-8')
            print named
            schedule(named)
    error_handle(path, obj_spider)
    os.remove('list_error.txt')


# 多线程的格式预处理
def list_handle(filename):
    name_list = []
    no = []
    with open(filename) as fout:
        for name in fout:
            if name[:3] == codecs.BOM_UTF8:
                name = name[3:]
            named = name.strip('.\n').decode('utf-8')
            print named
            name_list.append(named)
            no.append(None)
    pool = threadpool.ThreadPool(4)
    requests = threadpool.makeRequests(schedule, name_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()


def list_multiprocess(filename):
    name_list = []

    with open(filename) as fout:
        for name in fout:
            if name[:3] == codecs.BOM_UTF8:
                name = name[3:]
            named = name.strip('.\n').decode('utf-8')
            print named
            name_list.append(named)

    pool = ThreadPool(4)
    results = pool.map(process, name_list)
    pool.close()
    pool.join()



def error_handle(path, obj_spider):
    if os.path.exists('list_error.txt'):
        print('start list_error download')
        with open('list_error.txt') as fout:
            for name in fout:
                if name[:3] == codecs.BOM_UTF8:
                    name = name[3:]
                named = name.strip('.\n').decode('utf-8')
                print(named)
                schedule(path, named, obj_spider)
        print(datetime.datetime.now())
        print('all down')


def job_period():
    # ip_pool.ip_collect()
    list_handle('D:\\WechatList.txt')
    error_handle(path, SpiderMain())
    os.remove('list_error.txt')




if __name__ == "__main__":
    # logging.basicConfig()
    # sched = BlockingScheduler()
    # sched.add_job(job_period, 'cron', start_date='2016-09-01', hour=0, minute=0, second=1, end_date='2016-11-30')
    # a = sched.get_jobs()
    # print(a)
    # sched.start()
    # os.remove('list_error.txt')
    job_period()

    # list_multiprocess('D:\\WechatList.txt')
    # single_job('D:\\WechatList.txt', u'd:\\wechat_data1')


