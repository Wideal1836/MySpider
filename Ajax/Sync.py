'''
目标网址：https://spa5.scrape.center/
爬取内容：
1.都是Ajax请求，那么数据都是结构化的，直接拿出来就行了

详情页规律：https://spa5.scrape.center/api/book/7952978 每本书的地址都一样，唯独最后这串看不懂是数字，那么最后这串数字是哪来的？
列表页规律：https://spa5.scrape.center/api/book/?limit=18&offset=0  列表页的数据能和那串数字关联上，多观察几页看看能发现什么规律。
把数据保存在MONGODB
'''
import requests
from requests.exceptions import RequestException
import logging
import pymongo
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
INDEX_URL = 'https://spa5.scrape.center/api/book/?limit=18&offset={offset}'
DETAIL_URL = 'https://spa5.scrape.center/api/book/{id}'
LIMIT = 18
MAX_PAGE = 5

MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGO_DATABASE = 'spa5_books'
MONGO_COLLECTION = 'books(sync)'

client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
database = client[MONGO_DATABASE]
collection = database[MONGO_COLLECTION]


def scrapy_api(url):
    logging.info('start scraping %s', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error('get invalid statu code %s while scraping %s', response.status_code, url)
    except RequestException:
        logging.error('error occurred while scraping %s', url)


def scrapy_index(page):
    index_url = INDEX_URL.format(offset=LIMIT*(page-1))
    return scrapy_api(index_url)


def scrapy_detail(id):
    detail_url = DETAIL_URL.format(id=id)
    return scrapy_api(detail_url)


def save_data(data):
    logging.info('saving %s', data)
    if data:
        return collection.update_one({
            'id': data.get('id')
        }, {
            '$set': dict(data)
        }, upsert=True)


def main(page):
    index_datas = scrapy_index(page)
    results = index_datas['results']
    ids = []
    for result in results:
        id = result.get('id')
        ids.append(id)
    for id in ids:
        detail_datas = scrapy_detail(id)
        save_data(detail_datas)


if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pages = range(1, MAX_PAGE+1)
    pool.map(main, pages)
    pool.close()
    pool.join()
    print('运行结束!')