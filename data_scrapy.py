# -*- coding: utf-8 -*-
# author:           inspurer(月小水长)
# pc_type           lenovo
# create_date:      2019/2/27
# file_name:        lianjia_crawler.py
# github            https://github.com/inspurer
# qq_mail           2391527690@qq.com

import requests

from pyquery import PyQuery as pq

import time

import json

import threadpool

import threading


def get_list_page_url(city):

    start_url = "https://{}.lianjia.com/ershoufang".format(city)
    headers =  {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    try:
        response = requests.get(start_url, headers=headers)
        # print(response.status_code, response.text)
        doc = pq(response.text)
        total_num =  int(doc(".resultDes .total span").text())
        total_page = total_num // 30 + 1
        # 只能访问到前一百页
        if total_page > 100:
            total_page = 100

        page_url_list = list()

        for i in range(total_page):
            url = start_url + "/pg" + str(i + 1) + "/"
            page_url_list.append(url)
            #print(url)
        return page_url_list

    except:
        print("获取总套数出错,请确认起始URL是否正确")
        return None


detail_list = list()
lock = threading.Lock()


def page_and_detail_parser(page_url):
    global detail_list,lock
    headers =  {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Referer': 'https://bj.lianjia.com/ershoufang'
    }

    response = requests.get(page_url,headers=headers,timeout = 3)
    doc = pq(response.text)
        # broswer.get(page_url)
        # print(page_url)
        # doc = pq(broswer.page_source)
    for item in doc(".sellListContent > li").items():
        child_item = item(".noresultRecommend")
        detail_url = child_item.attr("href")
        print(detail_url)
        try:
            response = requests.get(url=detail_url, headers=headers,timeout = 3)
            detail_dict = dict()
            doc = pq(response.text)
            unit_price = doc(".unitPriceValue").text()
            unit_price = unit_price[0:unit_price.index("元")]
            title = doc("h1").text()
            area = doc(".areaName .info a").eq(0).text().strip()
            url = detail_url
            detail_dict["title"] = title
            detail_dict["area"] = area
            detail_dict["price"] = unit_price
            detail_dict["url"] = url
            lock.acquire()
            detail_list.append(detail_dict)
            lock.release()
            print(unit_price, title, area)
        except:
            print("获取详情页出错")

def save_data(data,filename):
    with open(filename+".json", 'w', encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))

def main():

    city_list = ['bj']
    for city in city_list:

        page_url_list = get_list_page_url(city)

        pool = threadpool.ThreadPool(10)
        requests = threadpool.makeRequests(page_and_detail_parser, page_url_list)
        [pool.putRequest(req) for req in requests]
        pool.wait()

        print(detail_list)

        save_data(detail_list,city)
        detail_list.clear()

if __name__ == '__main__':
    old = time.time()
    main()
    print("程序共运行{}s".format(time.time()-old))






