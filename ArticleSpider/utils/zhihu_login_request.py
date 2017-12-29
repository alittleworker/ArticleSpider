# -*- coding: utf-8 -*-

import request
import http.cookiejar as cookielib
import re

def zhihu_login(account, password):
    #知乎登录
    if re.match("^1\d{10}", account):
        post_url = ""