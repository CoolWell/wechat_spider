#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import requests
import html_parser
import urllib2
from ruokuaicode import RClient
import exceptions
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import filecache
import time
import os
import random
import datetime
import config
import socket
import sys
import logging
try:
    import StringIO


    def readimg(content):
        return Image.open(StringIO.StringIO(content))
except ImportError:
    import tempfile


    def readimg(content):
        f = tempfile.TemporaryFile()
        f.write(content)
        return Image.open(f)

UA = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
PROXY = "123.56.238.200:8123"
PSIPHON = '127.0.0.1:54552'

def test():
    profile_dir = r"D:\MyChrome\Default"
    # 设置请求头
    # "Referer": "http://weixin.sogou.com"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))
    PROXY = "123.56.238.200:8123"
    # j = random.randint(0, len(proxys)-1)
    # proxy = proxys[j]
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    # chrome_options.add_extension('')添加crx扩展
    # service_args = ['--proxy=localhost:9050', '--proxy-type=socks5', ]
    driver = webdriver.Chrome(r'C:\Python27\chromedriver', chrome_options=chrome_options)
    driver.get('http://icanhazip.com')
    driver.refresh()
    print(driver.page_source)
    driver.quit()


class HtmlDownloader(object):
    def __init__(self):
        self._ocr = RClient(config.dama_name, config.dama_pswd, config.dama_soft_id, config.dama_soft_key)
        self._cache = filecache.WechatCache(config.cache_dir, 60 * 60)
        self._session = self._cache.get(config.cache_session_name) if self._cache.get(
            config.cache_session_name) else requests.session()
        self.cookie = self.maintain_cookies_ph()
        self.agents = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            ]

    def ocr4wechat(self, url):
        # logger.debug('vcode appear, using _ocr_for_get_gzh_article_by_url_text')
        timestr = str(time.time()).replace('.', '')
        timever = timestr[0:13] + '.' + timestr[13:17]
        codeurl = 'http://mp.weixin.qq.com/mp/verifycode?cert=' + timever
        coder = self._session.get(codeurl)
        if hasattr(self, '_ocr'):
            result = self._ocr.create(coder.content, 2040)
            img_code = result['Result']
            print(img_code)
        else:
            im = readimg(coder.content)
            im.show()
            img_code = raw_input("please input code: ")
        post_url = 'http://mp.weixin.qq.com/mp/verifycode'
        post_data = {
            'cert': timever,
            'input': img_code
        }
        headers = {
            "User-Agent": random.choice(self.agents),
            'Host': 'mp.weixin.qq.com',
            'Referer': url
        }
        rr = self._session.post(post_url, post_data, headers=headers)
        print(rr.text)
        remsg = eval(rr.text)
        if remsg['ret'] != 0:
            # logger.error('cannot verify get_gzh_article  because ' + remsg['errmsg'])
            raise exceptions.WechatSogouVcodeException('cannot verify wechat_code  because ' + remsg['errmsg'])
        self._cache.set(config.cache_session_name, self._session)
        # logger.debug('ocr ', remsg['errmsg'])

    def download_list(self, url, name):
        '''
        使用urllib2 获取微信公众号列表页的url
        :param url:
        :param name:
        :return:
        '''
        headers = {
            "User-Agent": random.choice(self.agents),
            "Referer": 'http://weixin.sogou.com/',
            'Host': 'weixin.sogou.com',
            'Cookie': random.choice(self.cookie)
        }
        req = urllib2.Request(url, headers=headers)
        req.set_proxy(PROXY, 'http')
        try:
            response = urllib2.urlopen(req)
            time.sleep(1)
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                #HTTPError and URLError all have reason attribute.
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                #Only HTTPError has code attribute.
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
            return
        try:
            a = html_parser.HtmlParser.parse_list_url(response, name)
        except AttributeError:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
            return
        if a is not None:
            return self.download(a, name, url)

        # headers_weixin = {
        #     "User-Agent": random.choice(self.agents),
        #     "Referer": 'http://weixin.sogou.com/',
        #     'Host': 'mp.weixin.qq.com',
        # }
        # req1 = urllib2.Request(a, headers=headers_weixin)
        # response1 = urllib2.urlopen(req1)
        # with open('c:\\a.html', 'a') as f:
        #     f.write(response1.read())

    def download(self, link, name, url):
        """
        下载指定公众号的文章列表
        :param link:
        :param name:
        :param url:
        :return:
        """
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            random.choice(self.agents)
        )
        dcap["takesScreenshot"] = False
        dcap["phantomjs.page.customHeaders.Cookie"] = random.choice(self.cookie)
        # dcap["phantomjs.page.settings.resourceTimeout"] = ("1000")
        try:
            driver1 = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no', ])
        except Exception as e:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
            print(datetime.datetime.now())
            print(url)
            print(e)
        else:
            try:
                driver1.set_page_load_timeout(20)
                driver1.get(link)
                b = True
                try:
                    driver1.find_element_by_class_name('page_verify')
                except:
                    b = False

                if b is True:
                    print('page needs verify, stop the program')
                    print('the last weixinNUM is %s\n' % name)
                    self.ocr4wechat(link)
                    time.sleep(5)
                    with open(r'list_error.txt', 'a') as f:
                        f.write(name.encode('utf-8'))
                        f.write('\n')
                else:
                    html = driver1.page_source
                    return link, html
            except Exception as e:
                with open(r'list_error.txt', 'a') as f:
                    f.write(name.encode('utf-8'))
                    f.write('\n')
                print(url)
                print(datetime.datetime.now())
                print(e)

            finally:
                driver1.quit()

    def download_list_ph(self, url, name):
        '''
        使用phantomjs下载微信公众号文章列表
        :param url:
        :param name:
        :return:
        '''
        if url is None:
            return None

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            random.choice(self.agents)
        )
        dcap["takesScreenshot"] = False
        dcap["phantomjs.page.customHeaders.Cookie"] = random.choice(self.cookie)
        # dcap["phantomjs.page.settings.resourceTimeout"] = ("1000")
        a = True
        try:
            driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no',
                                                                                  '--proxy=123.56.238.200:8123'])
        except Exception as e:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
            print(datetime.datetime.now())
            print(url)
            print(e)

        else:
            driver.set_page_load_timeout(20)
            try:
                driver.get(url)
            except:
                time.sleep(2)
                driver.refresh()
            try:
                driver.find_element_by_id("noresult_part1_container")
                a = True
            except:
                a = False
            if a is True:
                with open(r'no_wechat.txt', 'a') as f:
                    f.write(name.encode('utf-8'))
                    f.write('\n')
            # 公众号存在
            elif a is False:
                try:
                    # driver.get_screenshot_as_file(r'c:\pic.png')
                    driver.implicitly_wait(2)
                    # 代理连接过多导致失败
                    button = driver.find_element_by_css_selector('a[uigs =\'main_toweixin_account_image_0\']')
                    link = button.get_attribute('href')
                    # with open(r'c:\WechatList.txt', 'a') as f:
                    #     f.write(name.encode('utf-8') + '\n')
                except Exception as e:
                    link = None
                    with open(r'list_error.txt', 'a') as f:
                        f.write(name.encode('utf-8'))
                        f.write('\n')
                    print(datetime.datetime.now())
                    print(url)
                    print(e)
                finally:
                    driver.quit()
        # 获取公众号文章列表
        if a is False and link is not None:
            try:
                driver1 = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
            except Exception as e:
                with open(r'list_error.txt', 'a') as f:
                    f.write(name.encode('utf-8'))
                    f.write('\n')
                print(datetime.datetime.now())
                print(url)
                print(e)
            else:
                try:
                    driver1.set_page_load_timeout(20)
                    driver1.get(link)
                    b = True
                    try:
                        driver1.find_element_by_class_name('page_verify')
                    except:
                        b = False

                    if b is True:
                        print('page needs verify, stop the program')
                        print('the last weixinNUM is %s\n' % name)
                        self.ocr4wechat(link)
                        time.sleep(5)
                        with open(r'list_error.txt', 'a') as f:
                            f.write(name.encode('utf-8'))
                            f.write('\n')
                        # os.system('pause')
                    else:
                        html = driver1.page_source
                        return link, html
                except Exception as e:
                    with open(r'list_error.txt', 'a') as f:
                        f.write(name.encode('utf-8'))
                        f.write('\n')
                    print(url)
                    print(datetime.datetime.now())
                    print(e)

                finally:
                    driver1.quit()

    def download_list_chrome(self, url, name):
        if url is None:
            return None
        profile_dir = r"D:\MyChrome\Default"
        # "Referer": "http://weixin.sogou.com"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        # chrome_options.add_extension('')添加crx扩展
        # service_args = ['--proxy=localhost:9050', '--proxy-type=socks5', ]
        try:
            driver = webdriver.Chrome(r'C:\Python27\chromedriver', chrome_options=chrome_options)
        except Exception as e:
            with open(r'list_error.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
            print(datetime.datetime.now())
            print(url)
            print(e)
        else:
            try:
                driver.set_page_load_timeout(20)
                try:
                    driver.get('http://weixin.sogou.com/')
                except:
                    time.sleep(3)
                    driver.refresh()
                # driver.implicitly_wait(5)
                # 会产生too many requests
                driver.delete_all_cookies()
                i = random.randint(0, 4)
                for cookie in self.cookie[i]:
                    driver.add_cookie(cookie)
                time.sleep(1)
                try:
                    driver.get(url)
                except:
                    time.sleep(2)
                    driver.refresh()
                time.sleep(2)
                # 判断是否存在这个公众号
                try:
                    driver.find_element_by_id("noresult_part1_container")
                    a = True
                except:
                    a = False
                if a is True:
                    with open(r'no_wechat.txt', 'a') as f:
                        f.write(name.encode('utf-8'))
                        f.write('\n')
                elif a is False:
                    # 应对 too many connections
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.ID, "sogou_vr_11002301_box_0"))
                        )
                    except:
                        time.sleep(2)
                        driver.refresh()
                    now_handle = driver.current_window_handle
                    driver.find_element_by_id('sogou_vr_11002301_box_0').click()
                    # 会存在需要验证的情况
                    time.sleep(2)
                    all_handles = driver.window_handles
                    for handle in all_handles:
                        if handle != now_handle:
                            driver.switch_to.window(handle)  # 跳转到新的窗口
                    # 判断页面是否是验证页面
                    # b = True
                    # while b is True:
                    # try:
                    #         driver.find_element_by_class_name("page_verify")
                    #         b = True
                    #         driver.refresh()
                    #         time.sleep(2)
                    #     except:
                    #         b = False
                    #
                    # # 等待列表的出现
                    # try:
                    #     WebDriverWait(driver, 5).until(
                    #         EC.presence_of_element_located((By.CLASS_NAME, "weui_msg_card_hd"))
                    #         )
                    # except:
                    #     driver.refresh()
                    #     time.sleep(2)
                    # html = driver.page_source#网页动态加载后的代码
                    wechat_url = driver.current_url
                    i = random.randint(0, 4)
                    dcap = dict(DesiredCapabilities.PHANTOMJS)
                    dcap["phantomjs.page.settings.userAgent"] = (
                        UA
                    )
                    dcap["takesScreenshot"] = (False)
                    dcap["phantomjs.page.customHeaders.Cookie"] = self.cookie[i]
                    try:
                        driver1 = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
                    except Exception as e:
                        with open(r'list_error.txt', 'a') as f:
                            f.write(name.encode('utf-8'))
                            f.write('\n')
                        print(datetime.datetime.now())
                        print(url)
                        print(e)
                    else:
                        try:
                            driver1.set_page_load_timeout(20)
                            driver1.get(wechat_url)
                            html = driver1.page_source
                            return wechat_url, html
                        # except Exception as e:
                        #     with open(r'list_error.txt', 'a') as f:
                        #         f.write(name.encode('utf-8'))
                        #         f.write('\n')
                        #     print(datetime.datetime.now())
                        #     print(url)
                        #     print(e)
                        finally:
                            driver1.quit()
                            # return wechat_url, html
            except Exception as e:
                with open(r'list_error.txt', 'a') as f:
                    f.write(name.encode('utf-8'))
                    f.write('\n')
                print(url)
                print(datetime.datetime.now())
                print(e)
            finally:
                driver.quit()
                # if a is False:
                # i = random.randint(0, 4)
                #     dcap = dict(DesiredCapabilities.PHANTOMJS)
                #     dcap["phantomjs.page.settings.userAgent"] = (
                #         UA
                #     )
                #     dcap["takesScreenshot"] = (False)
                #     dcap["phantomjs.page.customHeaders.Cookie"] = self.cookie[i]
                #     try:
                #         driver1 = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
                #     except Exception as e:
                #         print(datetime.datetime.now())
                #         print(url)
                #         print(e)
                #     else:
                #         try:
                #             driver1.set_page_load_timeout(20)
                #             driver1.get(wechat_url)
                #             html = driver1.page_source
                #             return wechat_url, html
                #         except Exception as e:
                #             print(datetime.datetime.now())
                #             print(url)
                #             print(e)
                #         finally:
                #             driver1.quit()



                # response = urllib2.urlopen(url)
                # if response.getcode() != 200:
                #     return None
                # return response.read()

    def download_articles_ph(self, url):
        '''
        使用phantomjs下载文章
        :param url: 文章链接
        :return:
        '''
        if url is None:
            return None
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            UA
        )
        dcap["takesScreenshot"] = (False)
        try:
            driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
        except Exception as e:
            print(datetime.datetime.now())
            print(url)
            print(e)
        else:
            try:
                driver.set_page_load_timeout(30)
                driver.get(url)
                time.sleep(1)
                # driver.implicitly_wait(2)
                html = driver.page_source
                return html
            except:
                print(datetime.datetime.now())
                print(url)
            finally:
                driver.quit()

    def download_articles_chrome(self, url):
        # service_args = ['--load-images=no', ]
        profile_dir = r"D:\MyChrome\Default"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--user-data-dir=" + os.path.abspath(profile_dir))
        # PROXY = "123.56.238.200:8123"
        # # j = random.randint(0, len(proxys)-1)
        # # proxy = proxys[j]
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)
        # chrome_options.add_extension('')添加crx扩展
        # service_args = ['--proxy=localhost:9050', '--proxy-type=socks5', '--load-images=no', ]
        try:
            driver = webdriver.Chrome(r'C:\Python27\chromedriver', chrome_options=chrome_options)
        except Exception as e:
            print(datetime.datetime.now())
            print(url)
            print(e)
        else:

            try:
                driver.set_page_load_timeout(30)
                driver.get(url)
                driver.implicitly_wait(2)
                html = driver.page_source
                return html
            except:
                print(datetime.datetime.now())
                print(url)
                # selenium.common.exceptions.TimeoutException:
                # return self.download_acticles(url)
                return None
            finally:
                driver.quit()

    def maintain_cookies(self):
        cookie = []
        # 获取5组cookies
        for i in range(5):
            driver = webdriver.Chrome(r'C:\Python27\chromedriver')
            driver.get("http://weixin.sogou.com/")
            # 获得cookie信息
            cookie.append(driver.get_cookies())
            print(driver.get_cookies())
            driver.quit()

        return cookie

    def maintain_cookies_ph(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = UA
        cookie = []
        # 获取5组cookies
        for i in range(5):
            driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no', ])
            driver.get("http://weixin.sogou.com/")
            # 获得cookie信息
            cookie.append(driver.get_cookies())
            # print(driver.get_cookies())
            driver.quit()
        return cookie


if __name__ == "__main__":
    a = HtmlDownloader()
    # # a.ocr4wechat('http://mp.weixin.qq.com/s?timestamp=1478687270&src=3&ver=1&signature=5RtOXxZ16P0x8hvN7sARkESooWCRi1F-'
    #              'AcdjyV1phiMF7EC8fCYB1STlGWMUeoUQtSoEFQC26jd-X-*3GiGa-ZwBJQBld54xrGpEc81g*kjGncNNXLgRkpw5WIoCO5T-KbO'
    #              'xjsRjYFvrvDaynu1I7vvIE9itjIEzCa77YZuMMyM=')
    # a.download_list_chrome("http://weixin.sogou.com/weixin?type=%d&query=%s" % (1, 'renmin'), u'renmin')

