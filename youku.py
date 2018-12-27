# -*- coding: UTF-8 -*-
import base64
import datetime
import json
import random
import re
import time
import urllib
import hmac

from http import cookies
from http import cookiejar
from inspect import isfunction

import log
from common import get_content
from common import VideoExtractor


class Youku(VideoExtractor):

    referer_youku = 'http://v.youku.com'

    stream_types = [
        {'id': 'hd3', 'container': 'flv', 'video_profile': '1080P'},
        {'id': 'hd3v2', 'container': 'flv', 'video_profile': '1080P'},
        {'id': 'mp4hd3', 'container': 'mp4', 'video_profile': '1080P'},
        {'id': 'mp4hd3v2', 'container': 'mp4', 'video_profile': '1080P'},

        {'id': 'hd2', 'container': 'flv', 'video_profile': '超清'},
        {'id': 'hd2v2', 'container': 'flv', 'video_profile': '超清'},
        {'id': 'mp4hd2', 'container': 'mp4', 'video_profile': '超清'},
        {'id': 'mp4hd2v2', 'container': 'mp4', 'video_profile': '超清'},

        {'id': 'mp4hd', 'container': 'mp4', 'video_profile': '高清'},
        # not really equivalent to mp4hd
        {'id': 'flvhd', 'container': 'flv', 'video_profile': '低清480P'},
        {'id': '3gphd', 'container': 'mp4', 'video_profile': '低清480P'},

        {'id': 'mp4sd', 'container': 'mp4', 'video_profile': '标清'},
        # obsolete?
        {'id': 'flv', 'container': 'flv', 'video_profile': '标清'},
        {'id': 'mp4', 'container': 'mp4', 'video_profile': '标清'},
    ]

    #User Agent
    keys = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19',
        'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        'Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
        'Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
        'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
        'Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3'
    ]

    def __init__(self):
        super().__init__()

        # User Agent
        #self.ua = self.__class__.mobile_ua
        self.ua = self.keys[random.randint(0, len(self.keys) - 1)]
        self.referer = self.__class__.referer_youku
        self.ccode = ''
        # Found in http://g.alicdn.com/player/ykplayer/0.5.64/youku-player.min.js

        self.utid = ""
        self.url = ""
        self.UpsUrl=""
        self.iput_url=""

        self.page = None
        self.video_list = None
        self.video_next = None
        self.password = None
        self.api_data = None
        self.api_error_code = None
        self.api_error_msg = None


    #从url中获取vid
    def get_vid_from_url(self):

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
                return self.vid

    #从网页内容中获取vid
    def get_vid_from_page(self):
        if not self.url:
            raise Exception('No url')
        self.page = get_content(self.url)
        b64p = r'([a-zA-Z0-9=]+)'
        str = 'videoId2: \'(.+)\''
        hit = re.search(str, self.page)
        if hit is not None:
            self.vid = hit.group(1)

    # 拼接ups链接
    def youku_ups(self):
        # + vid + ccode + client_ip + utid + client_ts + ckey + password
        url = 'https://ups.youku.com/ups/get.json?vid={}&ccode={}'.format(self.vid, self.ccode)
        url += '&client_ip=192.168.1.2'

        self.utid = self.fetch_cna()
        # self.utid = 'W59PmgAAACkDANk5JyfUl791'
        url += '&utid=' + self.utid

        #url += '&utid=' + self.getUtid().decode('utf-8')
        url += '&client_ts=' + str(int(time.time()))
        self.ckey = 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND'
        url += '&ckey=' + urllib.parse.quote(self.ckey) #编码操作

        if self.password_protected:
            url += '&password=' + self.password

        #创建请求头
        headers = dict(Referer=self.referer)
        headers['User-Agent'] = self.ua
        self.UpsUrl = url
        api_meta = json.loads(get_content(url, headers=headers))

        self.api_data = api_meta['data']
        data_error = self.api_data.get('error')
        if data_error:
            self.api_error_code = data_error.get('code')
            self.api_error_msg = data_error.get('note')


        if 'videos' in self.api_data:
            if 'list' in self.api_data['videos']:
                self.video_list = self.api_data['videos']['list']
            if 'next' in self.api_data['videos']:
                self.video_next = self.api_data['videos']['next']


    def youku_ups_TV(self):
        # + vid + ccode + client_ip + utid + client_ts + ckey + password
        url = 'https://ups.cp31.ott.cibntv.net/ups/get.json?vid={}&ccode={}'.format(self.vid,  self.ccode)
        url += '&client_ip=192.168.1.5'
        self.utid = self.fetch_cna()
        url += '&utid=' + self.utid
        url += '&client_ts=' + str(int(time.time()))

        #self.ckey = 'fdffd'
        self.ckey = '7B19C0AB12633B22E7FE81271162026020570708D6CC189E4924503C49D243A0DE6CD84A766832C2C99898FC5ED31F3709BB3CDD82C96492E721BDD381735026'
        url += '&ckey=' + urllib.parse.quote(self.ckey)  # 编码操作

        if self.password_protected:
            url += '&password=' + self.password

        # 创建请求头
        headers = dict(Referer=self.referer)
        headers['User-Agent'] = self.ua

        self.UpsUrl = url
        api_meta = json.loads(get_content(url, headers=headers))

        self.api_data = api_meta['data']
        data_error = self.api_data.get('error')
        if data_error:
            self.api_error_code = data_error.get('code')
            self.api_error_msg = data_error.get('note')

        if 'videos' in self.api_data:
            if 'list' in self.api_data['videos']:
                self.video_list = self.api_data['videos']['list']
            if 'next' in self.api_data['videos']:
                self.video_next = self.api_data['videos']['next']

    def fetch_cna(self):

        def quote_cna(val):
            if '%' in val:
                return val
            return urllib.parse.quote(val)

        cook = cookiejar.CookieJar()
        if cookies:
            for cookie in cook:
                if cookie.name == 'cna' and cookie.domain == '.youku.com':
                    log.i('Found cna in imported cookies. Use it')
                    return quote_cna(cookie.value)
        url = 'http://log.mmstat.com/eg.js'
        #url = 'http://gm.mmstat.com/yt/ykcomment.play.commentInit?cna='
        req = urllib.request.urlopen(url)
        headers = req.getheaders()
        for header in headers:
            if header[0].lower() == 'set-cookie':  #元组中第0项字符串转换为小写对比是不是'set-cookie'
                n_v = header[1].split(';')[0]       #根据分好分割出cna
                name, value = n_v.split('=')        #根据分好分割出cna字段
                if name == 'cna':
                    return quote_cna(value)
        log.w('It seems that the client failed to fetch a cna cookie. Please load your own cookie if possible')
        return quote_cna('DOG4EdW4qzsCAbZyXbU+t7Jt')

    def start(self):
        # print("请输入视频链接:")
        # iput_url = input()

        # print(iput_url)
        # print("===============================")

        self.url = self.iput_url

        if (self.get_vid_from_url() == None):
            self.get_vid_from_page()
            if (self.vid == None):
                print("找不到vid")

        #ccodelist = ['0401', "0505",  "050F", "0501", "0502","0510", "0502", "0507", "0508", "0512", "0513", "0514", "0503", "0590", '01010203', '0103010102', '0512']

        ccodelist = ["0502", "0503", "0590"]
        for ccode in ccodelist:
            self.ccode = ccode
            self.youku_ups()
            time.sleep(1)
            if self.api_data.get('stream') is not None:
                break

        if self.api_data.get('stream') is None:
            for ccode in ccodelist:
                self.ccode = ccode
                self.youku_ups_TV()
                if self.api_data.get('stream') is not None:
                    break

        if self.api_data.get('stream') is None:
            if self.api_error_msg:
                log.wtf(self.api_error_msg)
            else:
                log.wtf('Unknown error')

        self.title = self.api_data['video']['title']
        stream_types = dict([(i['id'], i) for i in self.stream_types])
        audio_lang = self.api_data['stream'][0]['audio_lang']

        for stream in self.api_data['stream']:
            stream_id = stream['stream_type']

            if stream_id in stream_types and stream['audio_lang'] == audio_lang:
                if 'alias-of' in stream_types[stream_id]:
                    stream_id = stream_types[stream_id]['alias-of']

                if stream_id not in self.streams:
                    self.streams[stream_id] = {
                        'container': stream_types[stream_id]['container'],
                        'video_profile': stream_types[stream_id]['video_profile'],
                        'size': stream['size'],
                        'pieces': [{
                            'segs': stream['segs']
                        }],
                        'm3u8_url': stream['m3u8_url']
                    }

                    src = []
                    for seg in stream['segs']:
                         src.append(seg['cdn_url'])
                    self.streams[stream_id]['src'] = src
                else:
                    self.streams[stream_id]['size'] += stream['size']
                    self.streams[stream_id]['pieces'].append({
                        'segs': stream['segs']
                    })
                    src = []
                    for seg in stream['segs']:
                        src.append(seg['cdn_url'])

                    self.streams[stream_id]['src'].extend(src)





















