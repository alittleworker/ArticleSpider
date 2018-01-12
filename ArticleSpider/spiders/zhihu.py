# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
import time

from urllib import parse
from selenium import webdriver
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem, ZhihuItemLoader


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/signup']

    # session = requests.session()
    # session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
    # try:
    #     session.cookies.load(ignore_discard=True)
    # except:
    #     print("cookie未能加载")

    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={1}&limit={2}"

    headers = {
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20",
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/question/",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="F:\selenium-driver\chromedriver.exe")
        super(ZhihuSpider, self).__init__()
        # dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_closed(self, spider):
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        #提取出首页/页面所有的url, 如果格式是 /question则提取
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            #如果是question页面，下载解析；不是，则继续检索跟踪(深度优先搜索)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, meta={"question_id":question_id}, callback=self.parse_question)
            else:
                yield scrapy.Request(url, callback=self.parse)


    def parse_question(self,response):
        #处理question页面，从页面提取数据
        question_id = int(response.meta.get("question_id",""))
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content","div.QuestionHeader-detail")
        item_loader.add_value("url",response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeaderActions button::text")
        item_loader.add_css("watch_user_num", "strong.NumberBoard-itemValue::attr(title)")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
        item_loader.add_value("crawl_time", datetime.datetime.now())

        question_item = item_loader.load_item()

        self.headers["Referer"] ="https://www.zhihu.com/question/" + str(question_id)
        yield scrapy.Request(self.start_answer_url.format(question_id, 0, 20), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = time.gmtime(answer["created_time"])
            answer_item["update_time"] = time.gmtime(answer["updated_time"])
            answer_item["crawl_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            yield answer_item

        if not is_end:
            yield scrapy.Request(url=next_url, headers= self.headers, callback=self.parse_answer)