'''
目标网址：:https://spa2.scrape.center/
爬取目标：
        1.url
        2.name
        3.categories
        4.cover
        5.score
        6.drama
保存至json文件
ajax请求都是经过加密的，常规方法无法进行爬取，一般情况都是逆向js或者借助自动化工具

'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from urllib.parse import urljoin
import multiprocessing
from os.path import exists
from os import makedirs
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://spa2.scrape.center/'
INDEX_URL = 'https://spa2.scrape.center/page/{page}'
MAX_PAGE = 10
TIME_OUT = 10

option = webdriver.ChromeOptions()
option.add_argument('--headless')
option.add_argument('blink-settings=imagesEnabled=false')

browser = webdriver.Chrome(options=option)
wait = WebDriverWait(browser, TIME_OUT)


def scrapy_api(url, condition, locator):
    logging.info('start scraping %s', url)
    try:
        browser.get(url)
        wait.until(condition(locator))
    except TimeoutException:
        logging.error('error occurred while scraping %s', url, exc_info=True)


def scrapy_index(page):
    index_url = INDEX_URL.format(page=page)
    scrapy_api(index_url, condition=EC.visibility_of_all_elements_located, locator=(By.CSS_SELECTOR, '#index .item'))


def parse_index():
    elements = browser.find_elements(By.CSS_SELECTOR, '#index .item .name')
    for element in elements:
        href = element.get_attribute('href')
        yield urljoin(INDEX_URL, href)


def scrapy_detail(detail_url):
    scrapy_api(detail_url, condition=EC.visibility_of_element_located, locator=(By.TAG_NAME, 'h2'))


def parse_detail():
    url = browser.current_url
    name = browser.find_element(By.CSS_SELECTOR, '.item .name h2').text
    cover = browser.find_element(By.CSS_SELECTOR, 'img.cover').get_attribute('src')
    categories = [element.text for element in browser.find_elements(By.CSS_SELECTOR, '.categories button span')]
    drama = browser.find_element(By.CSS_SELECTOR, '.drama p').text.strip()
    score = float(browser.find_element(By.CSS_SELECTOR, 'p.score').text)

    return {'url': url, 'name': name, 'cover': cover, 'categories':categories, 'drama': drama, 'score': score}


RESULT_DIR = 'selenium_result'
exists(RESULT_DIR) or makedirs(RESULT_DIR)


def save_data(data):
    name = data.get('name')
    path = f'{RESULT_DIR}/{name}.json'
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    logging.info('data saved successfully!')


def main(page):
    scrapy_index(page)
    detail_urls = parse_index()
    for detail_url in list(detail_urls):
        scrapy_detail(detail_url)
        data = parse_detail()
        logging.info('data %s', data)
        save_data(data)


if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pages = range(1, MAX_PAGE+1)
    pool.map(main, pages)
    pool.close()
    pool.join()
    browser.close()
    logging.info('你的小蜘蛛已运动结束!')
