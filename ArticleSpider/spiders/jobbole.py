# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    # start_urls = ['http://blog.jobbole.com/113343/']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    #收集伯乐在线所有404的url以及404页面数
    handle_httpstatus_list = [404, 302]

    def __init__(self):
        self.fail_urls = []

    def parse(self, response):
        """
        1.获取文章列表中的文章url并交给scrapy下载后进行解析
        2.获取下一页url并交给scrapy下载，下载完后交给parse函数
        """
        if response.status == 404 or response.status == 302:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")


        #解析页面文章url并交给scrapy下载后进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url  = post_node.css("::attr(href)").extract_first("")
            yield Request(url= parse.urljoin(response.url, post_url), meta={"front-img-url":image_url}, callback=self.parse_detail)
            print (post_url)

        #提取下一页url并交给scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def parse_detail(self, response):
        # article_item = JobBoleArticleItem()
        #提取文章的具体字段
        # front_image_url = response.meta.get("front-img-url", "")  #文章封面图url
        # title = response.xpath("//div[@class='entry-header']/h1/text()").extract_first(default="")
        # creat_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract_first().strip().replace("·","").strip()
        # praise_num = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract_first()
        # collect_num = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract_first()
        # match_re = re.match(".*?(\d+).*", collect_num)
        # if match_re:
        #     collect_num = int(match_re.group(1))
        # else:
        #     collect_num = 0
        #
        # comment_num = response.css(".btn-bluet-bigger.href-style.hide-on-480::text").extract_first()
        # match_re = re.match(".*?(\d+).*", comment_num)
        # if match_re:
        #     comment_num = int(match_re.group(1))
        # else:
        #     comment_num = 0
        #
        # content = response.xpath("//div[@class='entry']").extract_first()
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # article_item["front_image_url"] = [front_image_url]
        # try:
        #     creat_date = datetime.strptime(creat_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     creat_date = datetime.now().date()
        # article_item["creat_date"] = creat_date
        # article_item["praise_num"] = praise_num
        # article_item["collect_num"] = collect_num
        # article_item["comment_num"] = comment_num
        # article_item["content"] = content
        # article_item["tags"] = tags

        # 通过ItemLoder加载item
        front_image_url = response.meta.get("front-img-url", "")  # 文章封面图url
        item_loder = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loder.add_xpath("title", "//div[@class='entry-header']/h1/text()")
        item_loder.add_xpath("creat_date", "//p[@class='entry-meta-hide-on-mobile']/text()")
        item_loder.add_xpath("praise_num", "//span[contains(@class, 'vote-post-up')]/h10/text()")
        item_loder.add_xpath("collect_num", "//span[contains(@class, 'bookmark-btn')]/text()")
        item_loder.add_css("comment_num", ".btn-bluet-bigger.href-style.hide-on-480::text")
        item_loder.add_xpath("content", "//div[@class='entry']")
        item_loder.add_xpath("tags", "//p[@class='entry-meta-hide-on-mobile']/a/text()")
        item_loder.add_value("url", response.url)
        item_loder.add_value("url_object_id", get_md5(response.url))
        item_loder.add_value("front_image_url", [front_image_url])

        article_item = item_loder.load_item()


        #传到pipeline
        yield article_item

