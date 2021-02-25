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
    name = "JAIR"
    allowed_domains=["jair.org"]
    start_urls = ['https://www.jair.org/index.php/jair/issue/archive']
  
    
    def parse(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('https://www.jair.org/index.php/jair/issue/view')):
                yield response.follow(url, callback=self.parse_list)
           
    def parse_list(self, response):
        urls = response.xpath('/html/body//a/@href').extract()
        for url in urls:
            if(url.startswith('https://www.jair.org/index.php/jair/article/view') and len(url)==54):
                yield response.follow(url, callback=self.info_parse)
                
    def info_parse(self, response):
        urls = response.xpath("/html/body//a[@class='galley-link btn btn-primary pdf']/@href").extract()
        for url in urls:
            title=response.css("h1::text").extract_first()
            download_url=url.replace("view","download")
            yield response.follow(download_url, callback=self.pdf_download, meta={'title':title,'link':response.url})
            
    def pdf_download(self, response):
        title=response.meta['title']
        link=response.meta['link']
        filename=response.url.split('/')[-2]+"_"+response.url.split('/')[-1]+".pdf"
        urllib.request.urlretrieve(response.url, filename)
        paperItem=PaperItem()
        paperItem['title']=response.meta['title']
        paperItem['link']=response.meta['link']
        paperItem['language']="EN_US"
        paperItem['last_modified_at']=round(time.mktime(time.strptime(response.headers['Date'].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z"))*1000)
        paperItem['crawled_at']=round(time.time()*1000)
        outputString = convert_pdf_to_txt(filename)
        paperItem['contents']=outputString
        yield paperItem
        os.remove(filename)
        

                
    
        
        