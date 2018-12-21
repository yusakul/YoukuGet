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
    #User Agent
    mobile_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
    referer_youku = 'http://v.youku.com'
    # Last updated: 2017-10-13

    # Last updated: 2017-10-13
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
        {'id': 'flvhd', 'container': 'flv', 'video_profile': '渣清'},
        {'id': '3gphd', 'container': 'mp4', 'video_profile': '渣清'},

        {'id': 'mp4sd', 'container': 'mp4', 'video_profile': '标清'},
        # obsolete?
        {'id': 'flv', 'container': 'flv', 'video_profile': '标清'},
        {'id': 'mp4', 'container': 'mp4', 'video_profile': '标清'},
    ]


    def __init__(self):
        super().__init__()

        # User Agent
        self.ua = self.__class__.mobile_ua
        self.referer = self.__class__.referer_youku
        self.ccode = ''
        # Found in http://g.alicdn.com/player/ykplayer/0.5.64/youku-player.min.js
        self.ckey = 'DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND'
        self.utid = ""
        self.url = ""
        self.UpsUrl=""

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
        #self.ccode = '0590'
        # + vid + ccode + client_ip + utid + client_ts + ckey + password
        url = 'https://ups.youku.com/ups/get.json?vid={}&ccode={}'.format(self.vid, self.ccode)
        url += '&client_ip=192.168.1.1'
        self.utid = self.fetch_cna()
        url += '&utid=' + self.utid
        #url += '&utid=' + self.getUtid().decode('utf-8')
        url += '&client_ts=' + str(int(time.time()))
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

        if 'video' in self.api_data:
            print('title:', self.api_data['video']['title'])
        if 'stream' in self.api_data:
            stream = self.api_data['stream']
            for j in stream:
                print("stream_type:", j['stream_type'])
                segs = j['segs']
                for k in segs:
                    print(k['cdn_url'])


    def youku_ups_TV(self):
        # + vid + ccode + client_ip + utid + client_ts + ckey + password
        url = 'https://ups.cp31.ott.cibntv.net/ups/get.json?vid={}&ccode={}'.format(self.vid,  self.ccode)
        url += '&client_ip=192.168.1.1'
        self.utid = self.fetch_cna()
        url += '&utid=' + self.utid
        url += '&client_ts=' + str(int(time.time()))

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
           # print("code:", self.api_error_code)
            #print("note:", self.api_error_msg)
        if 'videos' in self.api_data:
            if 'list' in self.api_data['videos']:
                self.video_list = self.api_data['videos']['list']
                for i in range(len(self.video_list)):
                    print(self.video_list[i]['title'])
                    stream = self.api_data['stream']
                    for j in stream:
                        print(j['m3u8_url'])

            if 'next' in self.api_data['videos']:
                self.video_next = self.api_data['videos']['next']



    def getUtid(self):
        randomInt = random.uniform(-2147483648,2147483648) #0x80000000
        str2 = '%d' % randomInt
        i = int(time.time())
        j = int(random.uniform(-2147483648,2147483648))
        listOfByte1 = self.aa(i);
        listOfByte2 = self.aa(j);
        List = listOfByte1 + listOfByte2
        List.append(3)
        List.append(0)
        List = List + self.aa(self.ca(str2))
        sign = self.get_signature(self.bb(List))
        List = List + self.aa(self.cb(sign))
        str1 = "".join(str(i) for i in List)
        return base64.b64encode(self.ba(str1).encode('utf-8'))



    def aa(self, paramInt):
        i = paramInt % 0x100
        paramInt = paramInt >> 8
        j = paramInt % 0x100
        paramInt = paramInt >> 8
        k = paramInt % 0x100
        paramInt = paramInt >> 8
        n = paramInt % 0x100
        list = [n, k, j, i];
        return list;

    def ba(self, List):
        str = ""
        for i in List:
            str =  str + i

        return str

    def bb(self, List):
        str = ""
        for i in List:
            str =  str + chr(i)

        return str

    def ca(self, paramString):
        i=0
        k=0
        if( len(paramString) <= 0 ):
            return k
        paramlist = list(paramString)
        List = list()
        for n in paramlist:
            List.append(ord(n))

        j=0
        while(1):
            k = i
            if(j >= len(List)-1):
                break;
            i = self.intval32(i*31 + List[j])
            j+=1

        return k

    def cb(self, paramString):
        i = 0
        k = 0
        if (len(paramString) <= 0):
            return k
        paramlist = list(paramString)
        List = list()
        for n in paramlist:
            List.append(n)

        j = 0
        while (1):
            k = i
            if (j >= len(List) - 1):
                break;
            i = self.intval32(i * 31 + List[j])
            j += 1

        return k



    def intval32(self, num):
        num = num & 0xFFFFFFFF
        p = num>>31
        if(p==1):
            num = num-1
            num = ~num
            num = num & 0xFFFFFFFF
            return num -1
        else:
            return  num

    def get_signature(self, str):
        key = "d6fc3a4a06adbde89223bvefedc24fecde188aaa9161";
        macStr = hmac.new(key.encode('utf-8'), str.encode('utf-8'), 'sha1').hexdigest()
        signature = base64.b64encode(macStr.encode('utf-8'))
        return signature

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














