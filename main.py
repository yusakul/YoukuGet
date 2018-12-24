# -*- coding: UTF-8 -*-

import sys
from time import sleep

from youku import *






you = Youku()

you.iput_url = 'http://v.youku.com/v_show/id_XNDkyODQwNjgw==.html'
you.iput_url = 'http://v.youku.com/v_show/id_XMTg2MDkwMjU2OA==.html?from=y1.3-movie-grid-1095-9921.217752.1-1'




you.start()

print("===============================")
print('UpsUrl:', you.UpsUrl)
print("===============================")

print('title:', you.title)

if '3gphd' in you.streams:
    stream_type = you.streams['mp4hd2v2']
    print("|格式: ", stream_type['container']," |清晰度: ", stream_type['video_profile'], "|大小: ",   int(stream_type['size']/1024/1024),"MB|")
    for i in stream_type['src']:
        print(i)



'''
stdout_backup = sys.stdout
log_file = open("C:\\Users\\tfs\\Desktop\\message.log", "w")
sys.stdout = log_file

log_file.close()
sys.stdout = stdout_backup

'''