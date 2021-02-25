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
import urllib.request 
import os


def convert_pdf_to_txt(file_path):
   rsrcmgr = PDFResourceManager()
   retstr = StringIO()
   codec = 'utf-8'
   laparams = LAParams()
   device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
   fp = open(file_path, 'rb')
   interpreter = PDFPageInterpreter(rsrcmgr, device)
   password = ""
   maxpages = 0
   caching = True
   pagenos = set()
   for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
       interpreter.process_page(page)
   fp.close()
   device.close()
   str = retstr.getvalue()
   retstr.close()
   return str


class Paperpider(CrawlSpider):
    name = "SCIENCEDIRECT"
    allowed_domains=["sciencedirect.com"]
    start_urls = ['https://www.sciencedirect.com/journal/progress-in-polymer-science/special-issues?page=1']
    
    def parse(self, response):
        urls = response.xpath('/html/body//*[@id="all-issues"]//a/@href').extract()
        for url in urls:
            if(url.startswith('/journal')):
                url="https://www.sciencedirect.com"+url
                yield response.follow(url, callback=self.paper_list)
    
    def paper_list(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('/science/article/pii') and url.endswith('.pdf')):
                pdf_link="https://www.sciencedirect.com"+url
                url="https://www.sciencedirect.com"+url[:38]
                yield response.follow(url, callback=self.info_parse, meta={'pdf_link':pdf_link})
     
    def info_parse(self, response):
        title=response.css("span.title-text::text").extract_first()
        pdf_link=response.meta['pdf_link']
        download_url=response.url+"/pdfft?isDTMRedir=true&download=true"
        filename=response.url.split('/')[-1]+".pdf"
        opener=urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(download_url, filename)
        paperItem=PaperItem()
        paperItem['title']=title
        paperItem['link']=pdf_link
        paperItem['language']="EN_US"
        paperItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        paperItem['crawled_at']=round(time.time()*1000)
        outputString = convert_pdf_to_txt(filename)
        paperItem['contents']=outputString
        yield paperItem
        os.remove(filename)
              
    
        
        