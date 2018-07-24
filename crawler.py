# coding=utf-8
from __future__ import unicode_literals
import logging
import os
import re
import time
import math

try:
    from urllib.parse import urlparse  # py3
except:
    from urlparse import urlparse  # py2

import pdfkit
import requests
from bs4 import BeautifulSoup



html_template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>
"""


url = "https://blog.goo.ne.jp/0424725533"


def getList(url):
    postNum = 0
    hrefList = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    div = soup.find('div',id="mod-categories",class_='module')
    list = div.find_all('span',class_='mod-cat-count')
    for span in list:
        num = float(int(span.string.replace('(', '').replace(')', '')))
        postNum = postNum + num
        pageNum = math.ceil(postNum/20)
    for i in range(1,pageNum + 1):
        href = 'https://blog.goo.ne.jp/0424725533/arcv/?page=' + str(i) + '&c=&st=1'
        hrefList.append(href)
    print('获得'+ str(len(hrefList)) +'页列表链接。')
    return hrefList


def getLink(href):
    htmlList = []
    post = 0
    postNum = 0
    print('解析：' + href + '列表中......')
    response = requests.get(href)
    soup = BeautifulSoup(response.content, "html.parser")
    div = soup.find('div',class_='entry-body-text')
    for li in div.find_all('li'):
        title = li.find('span').get_text()
        contains = title.find('東大大学院')
        if contains >= 0:
            html = li.a.get('href')
            htmlList.append(html)
    print('>> 获取' + str(len(htmlList)) + '篇文章')
    return htmlList


def getPage(html):
    response = requests.get(html)
    soup = BeautifulSoup(response.content, 'html.parser')
    body = soup.find('div',class_="entry")
    top = body.find('div',class_="entry-top")
    title = top.find('h3').get_text()
    time = top.find(class_='entry-top-info-time').get_text()
    cen = body.find('div',class_="entry-body")
    context = cen.find('div',class_="entry-body-text")
    title_loc = soup.new_tag("center")
    title_tag = soup.new_tag('h1')
    time_loc = soup.new_tag("center")
    title_tag.string = title
    title_loc.insert(1, title_tag)
    context.insert(0, title_loc)
    time_loc.insert(1,time)
    context.insert(1, time_loc)
    page = str(context)
    page = html_template.format(content=page).encode("utf-8")
    with open(title + ".html", 'wb') as f:
        f.write(page)
        print('>> 抓取文章，命名为：' + title)
    return title


def savePdf(file,name):
    options = {
    'page-size': 'B5',
    'margin-top': '15mm',
    'margin-right': '15mm',
    'margin-bottom': '15mm',
    'margin-left': '15mm',
    'encoding': "UTF-8",
    'custom-header': [('Accept-Encoding', 'gzip')],
    'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),],
    'minimum-font-size': '40',}
    pdfkit.from_file(file,name,options=options)


if __name__=="__main__":
    hrefList = getList(url)
    start = time.time()
    for href in hrefList:
        htmlList = getLink(href)
        for html in htmlList:
            title = getPage(html)
            file_path = './' + str(title) + '.html'
            file_name = str(title) + '.pdf'
            savePdf(file_path,file_name)
    total_time = time.time() - start
    print(u"总共耗时：%f 秒" % total_time)
