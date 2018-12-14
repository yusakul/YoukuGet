import socket
from http import cookies
from urllib import request
import logging
from common import *

def get_content(url, headers = {}, decoded = Ture):
    """通过发送HTTP GET请求获取URL的内容。
             参数：
            url：一个URL。
            headers：客户端使用的请求标头。
            decoded：是使用UTF-8还是使用Content-Type中指定的字符集解码响应正文。
        返回：
         内容为字符串。
       """

    #打印日志
    logging.debug('get-content：%s' % url)

    #用Request类构建了一个完整的请求
    req = request.Request(url, headers=headers)

    if cookies:
        cookies.add_cookie_header(req)      #添加cookie
        req.headers.update(req.unredirected_hdrs)

    response = urlopen_with_retry(req)



