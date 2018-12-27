# -*- coding: UTF-8 -*-

import sys
from time import sleep

from youku import *

if __name__ == '__main__':

    you = Youku()

    you.iput_url = 'http://v.youku.com/v_show/id_XMTg2MDkwMjU2OA==.html?from=y1.3-movie-grid-1095-9921.217752.1-1'
    you.iput_url = 'http://v.youku.com/v_show/id_XNDkyODQwNjgw==.html'

    you.start()

    print("===============================")
    print('UpsUrl:', you.UpsUrl)
    print("===============================")

    print('title:', you.title)

    for stream_type in you.streams:

        print("|类型：",stream_type, "|格式: ", you.streams[stream_type]['container'], " |清晰度: ", you.streams[stream_type]['video_profile'], "|大小: ",
              int(you.streams[stream_type]['size'] / 1024 / 1024), "MB|")
        print("m3u8_url:",you.streams[stream_type]['m3u8_url'])
        print('cnd_url:')
        for cdn_url in you.streams[stream_type]['src']:
            print(cdn_url)
        print("===============================")


