# -*- coding: UTF-8 -*-
from youku import *

def start():
    print("请输入视频链接:")
    #iput_url = input()
    iput_url = 'http://v.youku.com/v_show/id_XNDkyODQwNjgw==.html'
    #iput_url = 'https://v.youku.com/v_show/id_XMzUwMTYwMDM2MA==.html?spm=a2hmv.20009921.yk-slide-249196.5~5~5~5!2~A'
    print(iput_url)
    print("===============================")

    you = Youku()
    you.url = iput_url

    if(you.get_vid_from_url() == None):
       you.get_vid_from_page()
       if(you.vid == None):
           print("找不到vid")

    #you.youku_ups()
    #you.youku_ups_TV()

    ccodelist = ['0401',"0510", "0502", "0507", "0508", "0512", "0513", "0514", "0503", "0590", '01010203','0103010102' ,'0512']
    for ccode in ccodelist:
        you.ccode = ccode
        you.youku_ups()
        if you.api_data.get('stream') is not None:
            break

    if you.api_data.get('stream') is None:
        for ccode in ccodelist:
            you.ccode = ccode
            you.youku_ups_TV()
            if you.api_data.get('stream') is not None:
                break

    if you.api_data.get('stream') is None:
        if you.api_error_msg:
            log.wtf(you.api_error_msg)
        else:
            log.wtf('Unknown error')


    print("===============================")
    print('UpsUrl:', you.UpsUrl)
    print("===============================")

start()



