import logging
import re
import socket
from http import cookies
from http import cookiejar
from urllib import request, parse, error
import ssl

class VideoExtractor():
    def __init__(self, *args):
        self.url = None
        self.title = None
        self.vid = None
        self.m3u8_url = None
        self.streams = {}
        self.streams_sorted = []
        self.audiolang = None
        self.password_protected = False
        self.dash_streams = {}
        self.caption_tracks = {}
        self.out = False
        self.ua = None
        self.referer = None
        self.danmuku = None

        if args:
            self.url = args[0]




def urlopen_with_retry(*args):
    retry_time = 3  #重试的次数
    for i in range(retry_time):
        try:
            return request.urlopen(*args)
        except socket.timeout as e:
            logging.debug('request attempt %s timeout' % str(i + 1))
            if i + 1 == retry_time:
                raise e
            # try to tackle youku CDN fails
        except error.HTTPError as http_error:
            logging.debug('HTTP Error with code{}'.format(http_error.code))
            if i + 1 == retry_time:
                raise http_error

#获取连接后的回复正文
def get_content(url, headers = {}, decoded = True):
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
    cookies = cookiejar.CookieJar()
    if cookies:
        cookies.add_cookie_header(req)   #添加cookie
        req.headers.update(req.unredirected_hdrs)

    response = urlopen_with_retry(req)

    data = response.read()      #读取回复



    #处理HTTP包gzip 和 deflate包
    # Handle HTTP compression for gzip and deflate (zlib)
    content_encoding = response.getheader('Content-Encoding')
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

    #解码回复正文
    if decoded:
        charset = match1(
            response.getheader('Content-Type', ''), r'charset=([\w-]+)'
        )
        if charset is not None:
            data = data.decode(charset)
        else:
            data = data.decode('utf-8', 'ignore')

    return data

#解包
def ungzip(data):
    """Decompresses data for Content-Encoding: gzip.
    """
    from io import BytesIO
    import gzip
    buffer = BytesIO(data)
    f = gzip.GzipFile(fileobj=buffer)
    return f.read()

#解包
def undeflate(data):
    """Decompresses data for Content-Encoding: deflate.
    (the zlib compression is used.)
    """
    import zlib
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data)+decompressobj.flush()


#匹配字符串
def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).
        通过字符串扫描匹配某些模式的子串（仅限第一个子组）。
    Args:
        text: A string to be scanned.要扫描的字符串。
        patterns: Arbitrary number of regex patterns.任意数量的正则表达式模式。

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        如果只有一个匹配，则返回一个字符串（如果未找到匹配项，则返回None）。
        When more than one pattern are given, returns a list of strings ([] if no match found).
         如果有多个匹配，则返回字符串列表（如果未找到匹配项，则返回[]）。
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret



