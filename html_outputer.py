#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import csv
import datetime
import os
import codecs



class HtmlOutputer(object):

    def __init__(self):
        self.datas = {}


    def collect_data(self, data):
        if data is None:
            return
        # data = (title, date, content, readNum, praise_num, discuss_content, discuss_praise)
        self.datas['title'] = data[0].encode('utf-8')
        self.datas['date'] = data[1].encode('utf-8')
        self.datas['content'] = data[2].encode('utf-8')
        self.datas['readNum'] = data[3].encode('utf-8')
        self.datas['praise_num'] = data[4].encode('utf-8')
        self.datas['discuss_content'] = [a.encode('utf-8') for a in data[5]]
        self.datas['discuss_praise'] = [a.encode('utf-8') for a in data[6]]
        return

    def clear_data(self):
        self.datas.clear()

    def output_html(self):
        fout = open('output.html', 'w')
        # fout.write("<html>")
        # fout.write("<body>")
        # fout.write("<table>")
        #
        # # for data in self.datas:
        # #     fout.write("<tr>")
        # #     fout.write("<td>%s</td>" % data['url'])
        # #     fout.write("<td>%s</td>" % data['title'].encode('utf-8'))
        # #     fout.write("<td>%s</td>" % data['summary'].encode('utf-8'))
        # #     fout.write("</tr>")
        # # fout.write("</table>")
        # # fout.write("</body>")
        # # fout.write("</html>")
        fout.close()

    def output_file(self, full_path, data):
        oneday = datetime.timedelta(days=1)
        today = str(datetime.date.today())
        file_name = full_path+r'\%s.csv' % today
        col = ['title', 'date', 'content', 'readNum', 'praise_num', 'discuss_content', 'discuss_praise']

        if os.path.exists(file_name):
            f = open(file_name, 'a')
        else:
            f = open(file_name, 'w')
            f.write(codecs.BOM_UTF8)

        for i in range(5):
            f.write(col[i])
            f.write(':')
            f.write(data[i])
            f.write('\n')
        for i, e in enumerate(data[5], start=1):
            f.write('discuss_content %s:' % str(i))
            f.write(e)
            f.write('  ')
            f.write('discuss_praise %s:' % str(i))
            f.write(data[6][i-1])
            f.write('\n')
        f.write('\n')
        f.close()
        return

    def output_csv(self, full_path, data):
        today = str(datetime.date.today())
        file_name = full_path+r'\%s.csv' %today
        col = ['title', 'date', 'content', 'readNum', 'praise_num', 'discuss_content', 'discuss_praise']
        if os.path.exists(file_name):
            csvfile = file(file_name, 'ab')
            writer = csv.writer(csvfile, dialect='excel')
            # writer = csv.DictWriter(csvfile, col)
        else:
            with open(file_name,'w') as f:
                f.write(codecs.BOM_UTF8)
            csvfile = file(file_name, 'wb')
            writer = csv.writer(csvfile, dialect='excel')
            # writer = csv.DictWriter(csvfile, fieldnames=col)
            writer.writerow(col)
        print data
        writer.writerow(data)
        csvfile.close()
