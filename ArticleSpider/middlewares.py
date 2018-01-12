# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
from ArticleSpider.tools.crawl_xici_ip import GetIp


class ArticlespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):
    #随机更换userAgent
    def __init__(self,crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault('User-Agent', get_ua())
        # proxy_ip = GetIp().get_random_ip()
        # request.meta["proxy"] = proxy_ip


from selenium import webdriver
from scrapy.http import HtmlResponse
import time


#通过chrome请求动态网页
class JSPageMiddleware(object):

    def process_request(self, request, spider):
        if request.url == "https://www.zhihu.com/signup":
            spider.browser.get("https://www.zhihu.com/signup")
            time.sleep(2)
            spider.browser.find_element_by_css_selector(".SignContainer-switch span[data-reactid='93']").click()
            spider.browser.find_element_by_css_selector(".Login-content input[name='username']").send_keys("15811203865")
            spider.browser.find_element_by_css_selector(".SignFlow-password input[name='password']").send_keys("199310lcy015")
            spider.browser.find_element_by_css_selector(".Login-content button.SignFlow-submitButton").click()
            time.sleep(2)
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, request=request, encoding="utf-8")