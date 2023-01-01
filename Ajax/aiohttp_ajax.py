'''
目标网址：https://spa5.scrape.center/
爬取内容：
1.都是Ajax请求，那么数据都是结构化的，直接拿出来就行了

详情页规律：https://spa5.scrape.center/api/book/7952978 每本书的地址都一样，唯独最后这串看不懂是数字，那么最后这串数字是哪来的？
列表页规律：https://spa5.scrape.center/api/book/?limit=18&offset=0  列表页的数据能和那串数字关联上，多观察几页看看能发现什么规律。
把数据保存在MONGODB
'''

import asyncio
import aiohttp
import logging
from motor.motor_asyncio import AsyncIOMotorClient

INDEX_URL = 'https://spa5.scrape.center/api/book/?limit={limit}&offset={offset}'
DETAIL_URL = 'https://spa5.scrape.center/api/book/{id}'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

CONCURRENCY = 5
MAX_PAGE = 20
LIMIT = 18

semaphore = asyncio.Semaphore(CONCURRENCY)
session = None

MONGODB_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'sp5_books'
MONGODB_COLLECTION = 'books'

client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
database = client[MONGODB_DATABASE]
collection = database[MONGODB_COLLECTION]


async def scrapy_api(url):
    async with semaphore:
        try:
            logging.info('start scraping %s', url)
            async with session.get(url) as response:
                return await response.json()
        except aiohttp.ClientError:
            logging.error('error occurred while scraping %s', url, exc_info=True)


async def scrapy_index(page):
    url = INDEX_URL.format(limit=LIMIT, offset=LIMIT*(page-1))
    return await scrapy_api(url)


async def save_data(data):
    logging.info('saving data %s', data)
    if data:
        return await collection.update_one({
            'id': data.get('id')
        }, {
            '$set': dict(data)
        }, upsert=True)


async def scrapy_detail(id):
    url = DETAIL_URL.format(id=id)
    data = await scrapy_api(url)
    await save_data(data)


async def main():
    global session
    session = aiohttp.ClientSession()
    scrapy_index_tasks = [asyncio.ensure_future(scrapy_index(page)) for page in range(1, MAX_PAGE+1)]
    index_datas = await asyncio.gather(*scrapy_index_tasks)
    ids = []
    for index_data in index_datas:
        if not index_data: continue
        results = index_data.get('results')
        for result in results:
            id = result.get('id')
            ids.append(id)
    scrapy_detail_tasks = [asyncio.ensure_future(scrapy_detail(id)) for id in ids]
    await asyncio.wait(scrapy_detail_tasks)
    await session.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

