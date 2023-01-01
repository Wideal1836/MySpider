'''
目标网址：https://spa2.scrape.center/
爬取目标：
1.name
2.score
3.categories
4.cover
5.drama
保存为json文件

'''

from pyppeteer import launch, errors
import logging
import asyncio
import os
import json
import multiprocessing

INDEX_URL = 'https://spa2.scrape.center/page/{page}'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
TIME_OUT = 1000
TOTAL_PAGE = 10
WINDOW_WIDTH, WINDOW_HEIGHT = 1366, 768
HEADLESS = False
browser, tab = None, None

RESULT_DIRS = 'pyppeteer_result'
os.path.exists(RESULT_DIRS) or os.makedirs(RESULT_DIRS)


async def init():
    global browser, tab
    browser = await launch(headless=HEADLESS,
                           args=['--disable-infobars',
                                 f'--window-size={WINDOW_WIDTH}, {WINDOW_HEIGHT}'])
    tab = await browser.newPage()
    await tab.setViewport({'width': WINDOW_WIDTH, 'height': WINDOW_HEIGHT})


async def scrape_api(url, selector):
    logging.info('start scraping %s', url)
    try:
        await tab.goto(url)
        await tab.waitForSelector(selector, options={
            'timeout': TIME_OUT * 10
        })
    except errors.TimeoutError:
        logging.error('error occurred while scraping %s', url, exc_info=True)


async def scrape_index(page):
    index_url = INDEX_URL.format(page=page)
    selector = '.item .name'
    await scrape_api(index_url, selector)


async def parse_index():
    return await tab.querySelectorAllEval('.item .name', 'nodes => nodes.map(node => node.href)')


async def scrape_detail(url):
    selector = 'h2'
    await scrape_api(url, selector)


async def parse_detail():
    name = await tab.querySelectorEval('h2', 'node => node.innerText')
    score = await tab.querySelectorEval('p.score', 'node => node.innerText')
    categories = await tab.querySelectorAllEval('div.categories button span',
                                                'nodes => nodes.map(node => node.innerText)')
    cover = await tab.querySelectorEval('img.cover', 'node => node.src')
    drama = await tab.querySelectorEval('.drama p', 'node => node.innerText')

    score = float(score)
    categories = [i for i in categories] if categories else []
    drama = drama.strip()
    return {'name': name, 'score': score, 'categories': categories, 'cover': cover, 'drama': drama}


async def save_data(data):
    if not data:
        logging.error('data saving failed!')
    name = data.get('name')
    PATH = f'{RESULT_DIRS}/{name}.json'
    json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    logging.info('%s \ndata saved successfully!', data)


async def main(page):
    try:
        await init()
        await scrape_index(page)
        detail_urls = await parse_index()
        for detail_url in detail_urls:
            await scrape_detail(detail_url)
            data = await parse_detail()
            await save_data(data)
    finally:
        await browser.close()


def async_api(page):
    asyncio.get_event_loop().run_until_complete(main(page))


if __name__ == '__main__':
    pool = multiprocessing.Pool(5)
    pages = range(1, TOTAL_PAGE + 1)
    pool.map(async_api, pages)
    pool.close()
    pool.join()
    logging.info('程序已停止运行')
    # for page in range(1, TOTAL_PAGE+1):
    #     async_api(page)