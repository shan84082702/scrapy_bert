import scrapy
from News.items import NewsItem
import time
import re


class NewsSpider(scrapy.Spider):
    name = "USATODAY"
    allowed_domains=["www.usatoday.com"]
    start_urls = ['https://www.usatoday.com/', 'https://www.usatoday.com/news/', 'https://www.usatoday.com/news/coronavirus/', 'https://www.usatoday.com/news/race-in-america/', 'https://www.usatoday.com/elections/', 'https://www.usatoday.com/news/nation/', 'https://www.usatoday.com/news/politics/', 'https://www.usatoday.com/news/politics/', 'https://www.usatoday.com/news/weather/', 'https://www.usatoday.com/news/education/', 'https://www.usatoday.com/news/trump-impeachment-inquiry/', 'https://www.usatoday.com/news/health/', 'https://www.usatoday.com/sports/', 'https://www.usatoday.com/sports/nfl/', 'https://www.usatoday.com/sports/mlb/', 'https://www.usatoday.com/sports/nba/', 'https://www.usatoday.com/sports/nhl/', 'https://www.usatoday.com/sports/indycar/', 'https://www.usatoday.com/sports/wnba/', 'https://www.usatoday.com/sports/olympics/', 'https://www.usatoday.com/sports/tennis/', 'https://www.usatoday.com/sports/soccer/', 'https://www.usatoday.com/sports/nascar/', 'https://www.usatoday.com/entertainment/', 'https://www.usatoday.com/entertainment/movies/', 'https://www.usatoday.com/entertainment/celebrities/', 'https://www.usatoday.com/entertainment/tv/', 'https://www.usatoday.com/entertainment/music/', 'https://www.usatoday.com/life/', 'https://www.usatoday.com/life/parenting/', 'https://www.usatoday.com/life/food-dining/', 'https://www.usatoday.com/money/', 'https://www.usatoday.com/money/personal-finance/', 'https://www.usatoday.com/money/cars/', 'https://www.usatoday.com/money/retirement/', 'https://www.usatoday.com/money/investing/', 'https://www.usatoday.com/money/careers/', 'https://www.usatoday.com/tech/', 'https://www.usatoday.com/tech/gaming/', 'https://www.usatoday.com/tech/tips/', 'https://www.usatoday.com/travel/', 'https://www.usatoday.com/travel/destinations/', 'https://www.usatoday.com/travel/airline-news/', 'https://www.usatoday.com/travel/cruises/', 'https://www.usatoday.com/travel/experience-america/', 'https://www.usatoday.com/opinion/', 'https://www.usatoday.com/opinion/todaysdebate/', 'https://www.usatoday.com/opinion/cartoons/', 'https://www.usatoday.com/opinion/columnist/', 'https://www.usatoday.com/opinion/voices/']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://www.usatoday.com"+url
            yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        newsItem['language']="EN_US"
        newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        newsItem['crawled_at']=round(time.time()*1000)
        newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        