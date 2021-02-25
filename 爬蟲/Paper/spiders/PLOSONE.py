import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from Paper.items import PaperItem
import time
import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO, BytesIO

def readPDF(pdfFile):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(pdfFile, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    device.close()
    textstr = retstr.getvalue()
    retstr.close()
    return textstr


class Paperpider(CrawlSpider):
    name = "PLOSONE"
    allowed_domains=["journals.plos.org"]
    start_urls = ['https://journals.plos.org']
    
    def parse(self, response):
        for page_index in range(1, 3829):
            url='https://journals.plos.org/plosone/browse/social_sciences?page='+str(page_index)
            yield response.follow(url, callback=self.parse_list)
    
    def parse_list(self, response):
        #paperItem=PaperItem()
        #paperItem['contents']=response.url
        #yield paperItem
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/plosone/article')):
                url="https://journals.plos.org"+url
                yield response.follow(url, callback=self.info_parse)
                
    def info_parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/plosone/article/file?id=') and url.endswith('type=printable')):
                url="https://journals.plos.org"+url
                title=response.css('title::text').extract_first(default=response.url)
                yield response.follow(url, callback=self.pdf_parse, meta={'title':title,'link':response.url})
   
    def pdf_parse(self, response):
        paperItem=PaperItem()
        paperItem['title']=response.meta['title']
        paperItem['link']=response.meta['link']
        paperItem['language']="EN_US"
        paperItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        paperItem['crawled_at']=round(time.time()*1000)
        pdfFile = BytesIO(response.body)
        outputString = readPDF(pdfFile)
        paperItem['contents']=outputString 
        pdfFile.close()
        yield paperItem