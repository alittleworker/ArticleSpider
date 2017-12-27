# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    front_image_url = scrapy.Field()
    fromt_image_path = scrapy.Field()
    creat_date = scrapy.Field()
    praise_num = scrapy.Field()
    collect_num = scrapy.Field()
    comment_num = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()