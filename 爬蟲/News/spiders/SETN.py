import scrapy
from News.items import NewsItem
import time
import re

class NewsSpider(scrapy.Spider):
    name = "SETN"
    allowed_domains=["setn.com"]
    start_urls = ['https://www.setn.com/','https://www.setn.com/ViewAll.aspx?PageGroupID=0','https://www.setn.com/Catalog.aspx?PageGroupID=6','https://www.setn.com/Catalog.aspx?PageGroupID=41','https://www.setn.com/Catalog.aspx?PageGroupID=4','https://www.setn.com/Catalog.aspx?PageGroupID=65','https://www.setn.com/Catalog.aspx?PageGroupID=34','https://www.setn.com/Local.aspx','https://www.setn.com/Catalog.aspx?PageGroupID=5','https://www.setn.com/Catalog.aspx?PageGroupID=2','https://www.setn.com/Catalog.aspx?PageGroupID=7','https://star.setn.com/?pk_vid=a528e8ff61ba7faf159582801594e6d0','https://star.setn.com/viewall/hot','https://star.setn.com/category/45','https://star.setn.com/category/17','https://star.setn.com/category/63','https://star.setn.com/category/64','https://star.setn.com/category/46']
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/')):
                if(response.url.startswith('https://www.setn.com')):
                    url="https://www.setn.com"+url
                elif(response.url.startswith('https://star.setn.com/')):
                    url="https://star.setn.com/"+url
            if(url.startswith('http')):
                yield response.follow(url, callback=self.info_parse)
            
    def info_parse(self, response):
        newsItem=NewsItem()
        newsItem['title']=response.css('title::text').extract_first(default=response.url)
        newsItem['link']=response.url
        newsItem['language']="ZH_CHT"
        newsItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        newsItem['crawled_at']=round(time.time()*1000)
        newsItem['contents']=response.xpath('/html/body').extract()[0]
        yield newsItem
        
        
       