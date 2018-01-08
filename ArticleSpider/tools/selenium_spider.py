# -*- coding: utf-8 -*-

from selenium import webdriver
from scrapy.selector import Selector
import time

#设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs", prefs)

browser = webdriver.Chrome(executable_path="F:\selenium-driver\chromedriver.exe", chrome_options=chrome_opt)

# browser.get("https://www.zhihu.com/signup")
#
# browser.find_element_by_css_selector(".SignContainer-switch span[data-reactid='60']").click()
# browser.find_element_by_css_selector(".Login-content input[name='username']").send_keys("15811203865")
# browser.find_element_by_css_selector(".SignFlow-password input[name='password']").send_keys("199310lcy015")
# browser.find_element_by_css_selector(".Login-content button.SignFlow-submitButton").click()

# browser.get("https://www.oschina.net/blog")
browser.get("https://www.taobao.com")
time.sleep(3)

#phantomjs, 无界面的浏览器，多进程情况下phantomjs性能会下降很严重

for i in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight; return lenOfPage")
    time.sleep(1)

# print (browser.page_source)

# browser.quit()