#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import re
import urlparse
import datetime

from bs4 import BeautifulSoup


class HtmlParser(object):

    @staticmethod
    def parse_list_url(response, name):
        if response is None:
            return
        soup = BeautifulSoup(response, 'html.parser', )
        if soup.find(id="noresult_part1_container"):
            with open(r'no_wechat.txt', 'a') as f:
                f.write(name.encode('utf-8'))
                f.write('\n')
                return
        url = soup.find(uigs='main_toweixin_account_image_0').get('href')
        return url

    def parse_list(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return
        soup = BeautifulSoup(html_cont, 'html.parser', )
        # push_date = soup.find_all('div', class_="weui_msg_card_hd", limit=10)
        push_date = soup.find_all('div', class_="weui_msg_card_hd")
        # 日期比较
        oneday = datetime.timedelta(days=1)
        today = str(datetime.date.today()-oneday*3)
        # 判断时间
        # for a in push_date:
        #     push_date1 = str(datetime.datetime.strptime(a.get_text().encode('utf-8'), "%Y年%m月%d日"))[:10]
        #     if today == push_date1:
        #         new_urls = self._get_new_urls(page_url, soup, today)
        #         # print(new_urls)
        #         return new_urls
        # return
        new_urls = self._get_new_urls(page_url, soup, today)
        return new_urls



        # new_urls = self._get_new_urls(page_url, soup)
        # new_data = self._get_new_data(page_url, soup)
        # return new_urls, new_data

    def _get_new_urls(self, page_url, soup, today):
        # new_urls = set()
        # links = soup.find_all('a', href=re.compile(r"/view/\d+\.htm"))
        # for link in links:
        #     new_url = link['href']
        #     new_full_url = urlparse.urljoin(page_url, new_url)
        #     new_urls.add(new_full_url)

        # article = soup.find('div', class_='weui_msg_card_bd')
        # article1 = article.find_all('h4', class_='weui_media_title')
        # links = [link.get('hrefs') for link in article1]
        links = []
        article1 = soup.find_all('h4', class_='weui_media_title')#所有文章
        push_data = soup.find_all('p', class_= "weui_media_extra_info")#文章日期
        for date, article in zip(push_data, article1):
            z = date.get_text()
            index = z.find(u'日')
            push = z[:index+1].encode('utf-8')
            data1 = str(datetime.datetime.strptime(push, "%Y年%m月%d日"))[:10]
            if data1 >= today:
                links.append(article.get('hrefs'))
            elif data1 < today:
                break
        # print(links)

        new_urls = []
        for link in links:
            if link != '':
                full_url = urlparse.urljoin(page_url, link)
                new_urls.append(full_url)

        return new_urls

    def _get_new_data(self, page_url, soup):
        res_data = {}
        # url

        res_data['url'] = page_url
        # <dd class="lemmaWgt-lemmaTitle-title"><h1>Python</h1>
        title_node = soup.find('dd', class_= "lemmaWgt-lemmaTitle-title").find("h1")
        res_data['title'] = title_node.get_text()

        summary_node = soup.find('div', class_="lemma-summary")
        res_data['summary'] = summary_node.get_text()
        return res_data

    def _replace_html(self, s):
        """替换html‘&quot;’等转义内容为正常内容
        Args:
            s: 文字内容
        Returns:
            s: 处理反转义后的文字
        """
        s = s.replace('&#39;', '\'')
        s = s.replace('&quot;', '"')
        s = s.replace('&amp;', '&')
        s = s.replace('&gt;', '>')
        s = s.replace('&lt;', '<')
        s = s.replace('&yen;', '¥')
        s = s.replace('amp;', '')
        s = s.replace('&lt;', '<')
        s = s.replace('&gt;', '>')
        s = s.replace('&nbsp;', ' ')
        s = s.replace('\\', '')
        return s

    def parse_article(self, html):
        # <div class="rich_media_content " id="js_content">
        if html is None:
            return
        soup = BeautifulSoup(html, 'html.parser', )
        # today = str(datetime.date.today())
        # post_date = soup.find('em', id='post-date' )
        # if post_date == today:
        # get_text()返回的是unicode编码
        try:
            title = soup.find('h2', class_='rich_media_title').get_text().strip(' \n').encode('utf-8')
            wname = soup.find('a', id='post-user').get_text().encode('utf-8')
            date = soup.find('em', id='post-date').get_text().encode('utf-8')
            content = soup.find('div', class_='rich_media_content ').get_text().strip('\n').encode('utf-8')#文章内容
            readNum = None
            praise_num = None
            discuss_content = None
            discuss_praise = None
        except Exception as e:
            return None
        try:
            readNum = soup.find('span', id='sg_readNum3').get_text().encode('utf-8')
            praise_num = soup.find('span', id='sg_likeNum3').get_text().encode('utf-8')
            discuss_list = soup.find_all('li', class_='discuss_item')
            discuss_content = [a.find('div', class_='discuss_message_content').get_text().strip().encode('utf-8') for a in discuss_list]
            discuss_praise = [a.find('span', class_='praise_num').get_text().encode('utf-8') for a in discuss_list]
        except Exception as e:
            pass
            # print(e)

        return title, wname, date, content, readNum, praise_num, discuss_content, discuss_praise

    def parse_wechat(self, page_source):
        if page_source is None:
            return
        soup = BeautifulSoup(page_source, 'html.parser',).find('li', id='sogou_vr_11002301_box_0')
        account_name = soup.find('a', uigs='account_name_0').get_text().encode('utf-8')
        info = soup.find('p', class_='info')
        weixinhao = info.find('label').get_text().encode('utf-8')
        information = [text for text in info.stripped_strings]
        # sougou 更新 去掉平均阅读数
        # if len(information) == 3:
        #     num1, num2 = re.findall(u'[\\d]+', information[-1])
        # else:
        #     num1 = 'null'
        #     num2 = 'null'
        if len(information) == 3:
            num1 = re.findall(u'[\\d]+', information[-1])
        else:
            num1 = 'null'

        introduction = soup.find_all('dl')
        fuction = introduction[0].find('dd').get_text()
        identify = 'null'
        if len(introduction) > 1:
            if introduction[1].find('dt').get_text().find(u'认证') != -1:
                identify = introduction[1].find('dd').get_text()
        return account_name, weixinhao, num1, fuction, identify







