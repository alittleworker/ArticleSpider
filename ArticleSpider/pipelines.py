# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    #自定义json文件导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        # item转字符串
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closer(self, spider):
        self.file.close()


class MySqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'root', 'scrapy_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql="""
            insert into article_spider(title, creat_date, url, url_object_id)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,(item["title"], item["creat_date"], item["url"], item["url_object_id"]))
        self.conn.commit()


class MySqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbParms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            password =settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode  = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbParms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrorback(self.handle_error)#处理异常

    def handle_error(self, failure):
        print (failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                    insert into article_spider(title,creat_date,url,url_object_id,front_image_url,comment_num,collect_num,praise_num,tags,content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cursor.execute(insert_sql, (item["title"], item["creat_date"], item["url"], item["url_object_id"],item["front_image_url"], item["comment_num"], item["collect_num"], item["praise_num"], item["tags"], item["content"]))


class JsonExporterPipeline(object):
    # 调用scrapy提供的json exporter导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.expoter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.expoter.start_exporting()

    def process_item(self, item, spider):
        self.expoter.export_item(item)
        return item

    def close_spider(self, spider):
        self.expoter.finish_exporting()
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item

