'''
先理清楚目标和爬取思路在开始：
1.我的思路是先框架在详细实现功能（其实就是分工明确点，这样思绪不容易混乱），这样可以明确每个代码块要实现哪些功能。
（（1）这个网站是某个界类大佬搭建的，他的书真的值得看。错过就是遗憾。
（2）另外在用正则解析页面内容的时候，经常容易出错（因为经常发生堵塞所以利用日志还是非常重要的，可以相对精准的定位bug发生位置），我的选择是新建一个文件去测试正则表达式的抓取，
实际上css和xpath如果不是很熟练也可以用这招。）
目标网站：https://ssr1.scrape.center/
爬取内容：
        1.电影名称: name
        2.封面: cover
        3.类别: categories
        4.上映时间: published_at
        5.评分: score
        6.剧情简介: drama
保存为json文件
'''
import requests
import re
import logging
from requests.exceptions import RequestException
from urllib.parse import urljoin
import json
from os.path import exists
import os
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
BASE_URL = 'https://ssr1.scrape.center/'
MAX_PAGE = 10


def html_api(url):
    logging.info('start scraping %s', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else: logging.error('get invalid status code %s while scraping %s', response.status_code, url)
    except RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrape_index(page):
    index_url = f'{BASE_URL}page/{page}'
    return html_api(index_url)


def parse_index(index_html):
    pattern = re.compile('<a.*?href="/(detail/\d+)".*?name.*?>', re.S)
    href_list = re.findall(pattern, index_html)
    if href_list:
        for href in href_list:
            detail_url = urljoin(BASE_URL, href)
            logging.info('get detail url %s', detail_url)
            yield detail_url
    else: return []


def scrape_detail(detail_url):
    return html_api(detail_url)


def parse_detail(detail_html):
    name_pattern = re.compile(r'<h2.*?>(.*?)</h2>', re.S)
    cover_pattern = re.compile(r'<div.*?item.*?<a.*?<img.*?src="(.*?)".*?class="cover">', re.S)
    categories_pattern = re.compile(r'<button.*?category.*?<span>(.*?)</span>.*?</button>', re.S)
    published_at_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}.*?上映)', re.S)
    score_pattern = re.compile(r'<p.*?score.*?>(.*?)</p>', re.S)
    drama_pattern = re.compile(r'<div.*?drama.*?>.*?<p.*?>(.*?)</p>.*?</div>', re.S)

    name = re.search(name_pattern, detail_html).group(1).strip() if re.search(name_pattern, detail_html) else None
    cover = re.search(cover_pattern, detail_html).group(1).strip() if re.search(cover_pattern, detail_html) else None
    categories = re.findall(categories_pattern, detail_html) if re.findall(categories_pattern, detail_html) else []
    published = re.search(published_at_pattern, detail_html).group(1).strip() if re.search(published_at_pattern, detail_html) else None
    score = float(re.search(score_pattern, detail_html).group(1).strip()) if re.search(score_pattern, detail_html) else None
    drama = re.search(drama_pattern, detail_html).group(1).strip() if re.search(drama_pattern, detail_html) else None

    return {'name': name, 'cover': cover, 'categories': categories, 'published': published, 'score': score, 'drama': drama}


RESULT_DIR = 'result'
exists(RESULT_DIR) or os.makedirs(RESULT_DIR)


def save_data(data):
    name = data.get('name')
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    with open(f'{RESULT_DIR}/{name}.json', 'w', encoding='utf-8') as f:
        f.write(data_json)
        logging.info('data %s saved successfully!', name)


def main(page):
    index_html = scrape_index(page)
    detail_urls = parse_index(index_html)
    for detail_url in detail_urls:
        detail_html = scrape_detail(detail_url)
        data = parse_detail(detail_html)
        logging.info('data %s', data)
        save_data(data)


if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pages = range(1, MAX_PAGE+1)
    pool.map(main, pages)
    pool.close()
    pool.join()
    print('所有数据已经爬取成功了！')