# -*- coding:utf-8 -*-
import requests
import re
import csv
from threading import Thread
from queue import Queue
from lxml import etree
from urllib.parse import urljoin


def wjc_detect(url):
    class WJCspider(Thread):
        # 去重url
        SEENS = set()

        def __init__(self, url_queue: Queue, result_csv, web_url):
            super(WJCspider, self).__init__()
            self.url_queue = url_queue
            self.csv_write = result_csv
            self.web_url = web_url
            # 过滤js脚本，站内css
            self.filter_js_css = re.compile(r'<script[^>]*>.*?</script>|<style>.*?</style>', re.I | re.S)
            # 过滤html及空白字符正则
            self.filter_html = re.compile(r'</?[^>]+>|[\t\r\n]', re.I | re.S)
            # 本站链接正则
            self.link_re = re.compile(rf'{web_url}.*', re.I)
            # 过滤tag页面
            self.tagLink_re = re.compile('.*tag.*', re.I)
            self._headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/3.0; +http://www.baidu.com/search/spider.html)"
            }
            # 将txt文件里字符编程成正则
            self.filter_wjc = self.make_filter_re()

        def run(self) -> None:
            while True:
                try:
                    url = self.url_queue.get()
                    if url in self.SEENS:
                        continue
                    html = self.download(url)
                    self.SEENS.add(url)
                    if html is None:
                        continue
                    self.extract_links(html)
                    content = self.get_content(html)
                    self.match_wjc(url, content)
                finally:
                    self.url_queue.task_done()

        def download(self, url, retries=3):
            try:
                r = requests.get(url, headers=self._headers, timeout=10)
            except requests.Timeout:
                source = ''
                if retries > 0:
                    return self.download(url, retries - 1)
            except requests.RequestException as err:
                source = ''
                print(f"Download ERR:{url},错误信息：{err}")
            else:
                r.encoding = 'utf-8'
                source = r.text
            return source

        def extract_links(self, html):
            doc = etree.HTML(html)
            all_links = doc.xpath(
                './/a[not(contains(@href,"jpg")) and not(contains(@href,"#")) and not(contains(@href,"?")) and not(contains(@href,"png")) and not(contains(@href,"gif"))]/attribute::href')
            for link in all_links:
                link = urljoin(self.web_url, link)
                if not self.link_re.match(link):
                    continue
                if self.tagLink_re.search(link):
                    continue
                self.url_queue.put(link.strip())

        def match_wjc(self, url, content):
            print(f'正在检测页面：{url}')
            match = self.filter_wjc.findall(content)
            match_words = '|'.join(set(match))
            if match_words:
                print(f'包含违禁词：{match_words}')
                self.csv_write.writerow([match_words])
            if not match_words:
                print('无违禁词')

        def get_content(self, html: str):
            """
            过滤html字符,中文符号,只保留中文字符
            :param html:
            :return:
            """
            content = self.filter_js_css.sub('', html)
            content = self.filter_html.sub('', content)
            return content

        @staticmethod
        def make_filter_re():
            """
            将违禁词文件编译成正则表达式
            :return:
            """
            with open('trust/wjc_detection/filter.txt', 'r', encoding='utf-8') as f:
                filter_str = '|'.join([str.strip() for str in f])
            return re.compile(rf'({filter_str})')

    domian = url  # 修改成你要查询的网站
    queue_num = 1  # 线程数量，自己根据本机和服务器配置设置，别开太大，网站容易卡死
    link_queue = Queue()
    link_queue.put(domian)
    with open('OK.csv', 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        for i in range(queue_num):
            wjc = WJCspider(link_queue, csv_writer, domian)
            wjc.setDaemon = True
            wjc.start()
        link_queue.join()
    print('done')
