# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import time

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from datetime import datetime
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from ArticleSpider.utils.common import extract_num


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()

class ZhihuItemLoader(ItemLoader):
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

class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field(
        output_processor=Join(",")
    )
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    # create_time = scrapy.Field()
    # update_time = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field(
        output_processor=Join(",")
    )
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = self["topics"]
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0
        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time, update_time, crawl_time
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
              update_time=VALUES(update_time)
        """

        create_time = time.strftime("%Y-%m-%d %H:%M:%S", self["create_time"])
        update_time = time.strftime("%Y-%m-%d %H:%M:%S", self["update_time"])
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time, self["crawl_time"]
        )

        return insert_sql, params
