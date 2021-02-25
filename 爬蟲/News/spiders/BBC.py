import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "BBC"
    allowed_domains=["bbc.com"]
    start_urls = ['https://www.bbc.com/news', 'https://www.bbc.com/news/coronavirus', 'https://www.bbc.com/news/world', 'https://www.bbc.com/news/world/africa', 'https://www.bbc.com/news/world/australia', 'https://www.bbc.com/news/world/europe', 'https://www.bbc.com/news/world/latin_america', 'https://www.bbc.com/news/world/middle_east', 'https://www.bbc.com/news/world/us_and_canada', 'https://www.bbc.com/news/world/asia', 'https://www.bbc.com/news/world/asia/china', 'https://www.bbc.com/news/world/asia/india', 'https://www.bbc.com/news/uk', 'https://www.bbc.com/news/england', 'https://www.bbc.com/news/northern_ireland', 'https://www.bbc.com/news/scotland', 'https://www.bbc.com/news/wales', 'https://www.bbc.com/news/business', 'https://www.bbc.com/news/business-38507481', 'https://www.bbc.com/news/business/companies', 'https://www.bbc.com/news/business-22434141', 'https://www.bbc.com/news/business-11428889', 'https://www.bbc.com/news/business/business_of_sport', 'https://www.bbc.com/news/business/economy', 'https://www.bbc.com/news/business/global_car_industry', 'https://www.bbc.com/news/technology', 'https://www.bbc.com/news/science_and_environment', 'https://www.bbc.com/news/entertainment_and_arts', 'https://www.bbc.com/news/health', 'https://www.bbc.com/news/reality_check', 'https://www.bbc.com/news/newsbeat']
    
    def parse(self, response):
        #newsItem=NewsItem()
        #newsItem['contents']=response.url
        #yield newsItem
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                url="https://www.bbc.com"+url
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
        
        
       