# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from datetime import datetime


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


def add_jobbole(value):
    return value + "-jobbole"


def date_convert(value):
    try:
        create_date = datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.now().date()
    return create_date


def num_convert(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        value = int(match_re.group(1))
    else:
        value = 0
    return value


def remove_comment_tags(value):
    if "评论" not in value:
        return value


def return_value(value):
    return value


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(add_jobbole)
    )
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    creat_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    praise_num = scrapy.Field(
        input_processor=MapCompose(num_convert)
    )
    collect_num = scrapy.Field(
        input_processor=MapCompose(num_convert)
    )
    comment_num = scrapy.Field(
        input_processor=MapCompose(num_convert)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )