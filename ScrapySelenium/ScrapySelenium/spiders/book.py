import scrapy
from ..items import BookItem
from gerapy_selenium import SeleniumRequest

class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['spa5.scrape.center']
    base_url = 'https://spa5.scrape.center/'

    def start_requests(self):
        for page in range(1, 2):
            start_url = f"{self.base_url}page/{page}"
            yield SeleniumRequest(start_url, callback=self.parse_index, wait_for='.item .name')

    def parse_index(self, response):
        items = response.css('.item')
        for item in items:
            href = item.css('.top a::attr(href)').extract_first()
            detail_url = response.urljoin(href)
            yield SeleniumRequest(detail_url, callback=self.parse_detail, priority=2, wait_for='h2.name')

    def parse_detail(self, response):
        name = response.css('h2.name::text').extract_first()
        tags = response.css('div.tags button span::text').extract()
        score = response.css('.score::text').extract_first()
        cover = response.css('img.cover::attr(src)').extract_first()
        price = response.css('p.price span::text').extract_first()
        tags = [tag.strip() for tag in tags] if tags else []
        score = float(score.strip()) if score else None
        item = BookItem(name=name, tags=tags, score=score, cover=cover, price=price)
        yield item
