# -*- coding: utf-8 -*-

import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect('localhost', 'root', 'root', 'scrapy_spider', charset="utf8", use_unicode=True)
cursor = conn.cursor()


def crawl_ips():
    #爬取西刺的免费ip代理
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.154 Safari/537.36"}

    for i in range(2616):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar ::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_text = tr.css("td::text").extract()

            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]

            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            insert_sql = """
                insert into proxy_ip(ip, port, proxy_type, speed)
                VALUES ('{0}', '{1}', '{2}', '{3}')
            """
            cursor.execute(insert_sql.format(ip_info[0],ip_info[1],ip_info[2],ip_info[3]))
            conn.commit()


class GetIp(object):
    def delete_ip(self, ip):
        delete_sql = "delete from proxy_ip where ip='{0}'".format(ip)
        cursor.execute(delete_sql)
        conn.commit()

    def judge_ip(self, proxy_url):
        #判断ip是否可用
        http_url = "http://www.baidu.com"
        if "HTTPS" in proxy_url:
            proxy_dict ={
                "https":proxy_url,
            }
        else:
            proxy_dict = {
                "http": proxy_url,
            }
        try:
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            return False
        else:
            code = response.status_code
            if code >=200 and code<300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                return False

    def get_random_ip(self):
        get_sql = "SELECT proxy_type, ip, PORT FROM proxy_ip WHERE proxy_type is NOT NULL ORDER BY RAND() LIMIT 1"
        cursor.execute(get_sql)
        result = cursor.fetchall()[0]
        proxy_type = result[0]
        ip = result[1]
        port = result[2]

        proxy_url = "{0}://{1}:{2}".format(proxy_type, ip, port)

        if self.judge_ip(proxy_url):
            print(proxy_url)
            return proxy_url
        else:
            self.delete_ip(ip)
            print(proxy_url, " is false")
            return self.get_random_ip()

# print(crawl_ips())