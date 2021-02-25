# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
from scrapy import settings
import pymongo
"""
class NewsPipeline:
    # 連線資料庫
    
    def open_spider(self, spider):
        MONGODB_DB_NAME = "webpage_dataset"
        MONGODB_HOST = "fpgindexer2.widelab.org"
        MONGODB_PORT = 27021
        MONGODB_USER = "webpageDatasetMaster"
        MONGODB_PASSWORD = "webpageDatasetMasterPassword"
        
        db = MONGODB_DB_NAME
        host = MONGODB_HOST
        port = MONGODB_PORT
        user = MONGODB_USER
        password = MONGODB_PASSWORD
        
        db_uri = host
        db_name = db
        db_coll = "News"
        self.db_client = pymongo.MongoClient(host=host, port=port)
        db = self.db_client[db_name]
        db.authenticate(user, password)
        self.coll = db[db_coll]

    def process_item(self, NewsItem, spider):
        self.insert_article(NewsItem)
        return item

    def insert_article(self, NewsItem):
        item = dict(NewsItem)
        self.coll.insert_one(NewsItem)
"""
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class NewsPipeline:
    def process_item(self, item, spider):
        return item 

