import requests
import time
import json
from store_data import store_MongoDB
import multiprocessing
import threading
import re


def content_parse(key, cont):
    try:
        if key == 'main_content':
            content = json.loads(cont.content.decode())['data']
            return content
        elif key == 'followingNum_followerNum':
            content = json.loads(cont.content.decode()[6:-1])
            following_num = content['data']['following']
            follower_num = content['data']['follower']
            return (following_num, follower_num)
        elif key == 'view_and_read':
            content = json.loads(cont.content.decode()[6:-1])['data']
            view_num = content['archive']['view']
            read_num = content['article']['view']
            return (view_num, read_num)
        elif key == 'channel_content':
            content = json.loads(cont.content.decode()[6:-1])['data']
            return content
        elif key == 'vedio_lists':
            # 此处拿到的aid和  f'https://www.bilibili.com/video/av{aid}'获取视频
            content = json.loads(cont.content.decode())['data']['vlist']
            return content
        elif key == 'following':
            followiing_lists = json.loads(cont.content.decode()[6:-1])['data']['list']
            return followiing_lists
        elif key == 'follower':
            follower_lists = json.loads(cont.content.decode()[6:-1])['data']['list']
            return follower_lists
        else:
            return None
    except Exception as e:
        print(mid + '除了问题')


def get_content(mid):
    # 获取Bilibili的json用户数据url
    '''
    main_content = f"https://api.bilibili.com/x/space/acc/info?mid={mid}&jsonp=jsonp"
    card = f"https://api.bilibili.com/x/web-interface/card?mid={mid}&photo=true"
    followingNum_followerNum = f"https://api.bilibili.com/x/relation/stat?vmid={mid}&jsonp=jsonp&callback=__jp4"
    view_and_read = f"https://api.bilibili.com/x/space/upstat?mid={mid}&jsonp=jsonp&callback=__jp5"
    channel_content = f"https://api.bilibili.com/x/space/channel/list?mid={mid}&guest=false&jsonp=jsonp&callback=__jp6"
    person_index = f"https://api.bilibili.com/x/space/navnum?mid={mid}&jsonp=jsonp&callback=__jp7"
    vedio_lists = f"https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=200&tid=0&page=1&keyword=&order=pubdate"
    following = f"https://api.bilibili.com/x/relation/followings?vmid={mid}&pn=1&ps=20&order=desc&jsonp=jsonp&callback=__jp6"
    follower = f"https://api.bilibili.com/x/relation/followers?vmid={mid}&pn=1&ps=200&order=desc&jsonp=jsonp&callback=__jp6"
    '''
    url_dicts = {'main_content': f"https://api.bilibili.com/x/space/acc/info?mid={mid}&jsonp=jsonp",
                 # 发现与上一条url的内容重复
                 # 'card': f"https://api.bilibili.com/x/web-interface/card?mid={mid}&photo=true",
                 'followingNum_followerNum': f"https://api.bilibili.com/x/relation/stat?vmid={mid}&jsonp=jsonp&callback=__jp4",
                 'view_and_read': f"https://api.bilibili.com/x/space/upstat?mid={mid}&jsonp=jsonp&callback=__jp5",
                 'channel_content': f"https://api.bilibili.com/x/space/channel/list?mid={mid}&guest=false&jsonp=jsonp&callback=__jp6",
                 # 发现内容没什么用 ><-__-><
                 # 'person_index': f"https://api.bilibili.com/x/space/navnum?mid={mid}&jsonp=jsonp&callback=__jp7",
                 'vedio_lists': f"https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=20&tid=0&page=1&keyword=&order=pubdate",
                 'following': f"https://api.bilibili.com/x/relation/followings?vmid={mid}&pn=1&ps=200&order=desc&jsonp=jsonp&callback=__jp6",
                 'follower': f"https://api.bilibili.com/x/relation/followers?vmid={mid}&pn=1&ps=20&order=desc&jsonp=jsonp&callback=__jp6"
                 }
    items = {}
    for key, value in url_dicts.items():
        cont = requests.get(url=value, headers=headers)
        items[key] = content_parse(key, cont)
    return items


if __name__ == '__main__':
    mid = '395074625'
    headers = {
        "Referer": f"https://space.bilibili.com/{mid}/channel/index",
        "Sec-Fetch-Mode": "no-cors",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    }
    items = get_content(mid)
    store_MongoDB(items)
