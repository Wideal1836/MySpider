import requests
import re

response = requests.get('https://ssr1.scrape.center/detail/16')
detail_html = response.text

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
#
data = {'name': name, 'cover': cover, 'categories': categories, 'published': published, 'score': score, 'drama': drama}

print(data)