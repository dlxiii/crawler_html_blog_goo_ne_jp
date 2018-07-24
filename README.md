## 背景

* 考虑 Ms.Gao 刚刚与意愿教授谈过话，士气大增，复习计划箭在弦上。
* 而且，有贵人相助，提供了一些备考大学院的往年试题。
* 再者，据说她的入学考试比较难，时间紧急。
* 最后，我的阶段研究计划还未收尾。

**我决定拿出一个24小时的时间来学习并为 Ms. Gao 收集并整理题库**


<!--more-->


## 条件

题库博客一枚：https://blog.goo.ne.jp/0424725533
破笔记本一台：Mac OS
破腾讯云一朵：CentOS7
不太够的时间：24小时
基础水平劳动力：一名

## 目标

整理博客中所有 UT 大学院中数学部分的往年题库，并整理成 pdf。

## 参考

* https://foofish.net/crawler-beautifulsoup.html （主要启蒙读物）
* http://www.cnblogs.com/livingintruth/p/3473627.html （不止是腾讯云，ITO在mac上也是会broken pipe。）
* HTML 相关
* Python 相关

## 策略

* 通过右侧边栏的文章分类（category）计算博客中文章数目；除以20（20是每页文章列表数量）获得文章总页数。
* 检索文章列表，找出有'東大大学院'为标题的文章，并记录其链接，标题，发表时间。
* 抓取单页中文章内容并下载保存为html文件。
* 讲html文件转为pdf。

## 实现

~~~python
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
~~~

在 Mac的jupyter nootbook测试
总共耗时：636.350848 秒