# -*- coding: UTF-8 -*-

import re
from extractor import *


class Youku:
    #User Agent
    mobile_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
    referer_youku = 'http://v.youku.com'
    # Last updated: 2017-10-13


    def __init__(self):
        super().__init__()

        # User Agent
        self.ua = self.__class__.mobile_ua
        self.referer = self.__class__.referer_youku
        self.ccode = '5090'
        # Found in http://g.alicdn.com/player/ykplayer/0.5.64/youku-player.min.js
        self.ckey = 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND'
        self.utid = None


        #从url中获取vid
        def get_vid_form_url(self):
            # 不可靠 check #1633
            b64p = r'([a-zA-Z0-9=]+)'
            p_list = [r'youku\.com/v_show/id_' + b64p,
                      r'player\.youku\.com/player\.php/sid/' + b64p + r'/v\.swf',
                      r'loader\.swf\?VideoIDS=' + b64p,
                      r'player\.youku\.com/embed/' + b64p]
            if not self.url:
                raise Exception('No url')
            for p in p_list:
                hit = re.search(p, self.url)
                if hit is not None:
                    self.vid = hit.group(1)
                    return

        #从网页内容中获取vid
        def get_vid_from_page(self):
            if not self.url:
                raise Exception('No url')
            self.page = get_content(self.url)
            hit = re.search(r'videoId2:"([A-Za-z0-9=]+)"', self.page)
            if hit is not None:
                self.vid = hit.group(1)









