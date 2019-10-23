import urllib
import requests
import time
import json
import threading
import random
from config import user_agent_list
import dynamic_get_proxy
from store_data import store_MongoDB
from queue import Queue

# threading.Semaphore 使用PV操作
productor = threading.Semaphore(25)  # P productor.acquire() V productor.release()
resource = threading.Semaphore(200)
consumer = threading.Semaphore(0)
ERROR_LIST = []
que = Queue(200)
proxies_list = dynamic_get_proxy.get_proxies_list()
print(proxies_list)

class Crwal_Thread(threading.Thread):
    def __init__(self, name, mid_list):
        super(Crwal_Thread, self).__init__()
        self.name = name
        self.mid_list = mid_list

    def run(self):
        print(f"--------启动线程{self.name}--------")
        while 1:
            if not self.mid_list:
                break
            mid = self.mid_list.pop()
            get_content(mid)
            print(f'{self.name} 爬到了，已经返给队列')
        print(f"-------{self.name} is OK!!--------")


class Store_Thread(threading.Thread):
    def __init__(self, name):
        super(Store_Thread, self).__init__()
        self.name = name

    def run(self):
        print(f'-----{self.name}需要将存储数据到mangodb!-----')
        while True:
            # 解决生产者消费者模型中生产者慢、消费者快的问题
            # 先用if 解决
            # 在第5个版本中使用PV操作来来实现
            try:
                consumer.acquire()
                resource.acquire()
                items = que.get(True, 20)
                store_MongoDB(items)
                if que.empty():
                    time.sleep(120)
                    if que.empty():
                        break
                resource.release()
                productor.release()
                print(f'{self.name} 存储 is OK!')
            except Exception as e:
                print(e, '存储出现问题')
        print(f'------{self.name}存储线程结束-------')


def get_proxies():
    global proxies_list
    url = 'http://www.baidu.com/'
    proxies = {'https': random.choice(proxies_list)}
    r = requests.get(url=url, proxies=proxies)
    if r.status_code == 200:
        return proxies
    else:
        print('----------需要重新获取IP池------------')
        proxies_lists = dynamic_get_proxy.get_proxies_list()
        return {'https': random.choice(proxies_lists)}




def content_parse(mid, key, cont):
    # 此处加上一个time.sleep()来调整爬取的速率
    time.sleep(0.2)
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
        ERROR_LIST.append(mid)
        print(f'{str(mid)}除了问题')


def get_content(mid):
    # 获取Bilibili的json用户数据url
    headers = {
        "Referer": f"https://space.bilibili.com/{mid}/channel/index",
        "Sec-Fetch-Mode": "no-cors",
        "User-Agent": random.choice(user_agent_list),
    }
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
    items['mid'] = mid
    # 获取动态ip进行反爬虫策略
    # 如果刚好出现极端情况，还剩1s的proxies通过了之前的测试这里应该怎么处理？
    #proxies = get_proxies()
    for key, value in url_dicts.items():
        #cont = requests.get(url=value, headers=headers, proxies=proxies)
        cont = requests.get(url=value, headers=headers)
        items[key] = content_parse(mid, key, cont)
    productor.acquire(timeout=10)
    resource.acquire()
    que.put(items)
    resource.release()
    consumer.release()
    return items


def crawl_list(mid_list):
    th_lists = ['1号爬线程', '2号爬线程', '3号爬线程', '4号爬线程', '5号爬线程']
    td_lists = []
    for th in th_lists:
        td = Crwal_Thread(name=th, mid_list=mid_list)
        td_lists.append(td)
    return td_lists


def store_list():
    st_lists = ['1号存线程', '2号存线程', '3号存线程']
    stl_lists = []
    for st in st_lists:
        stl = Store_Thread(name=st)
        stl_lists.append(stl)
    return stl_lists


def main():
    # 使用多线程爬B站数据
    print('开始爬数据')
    # 开始爬mid= m 到 n 的用户数据
    for i in range(1, 15000):
        mid_list = list(range((i-1)*10000, i*10000))
        td_lists = crawl_list(mid_list)
        for td in td_lists:
            td.start()
        stl_lists = store_list()
        time.sleep(3)
        for stl in stl_lists:
            stl.start()

        for td in td_lists:
            td.join()

        for stl in stl_lists:
            stl.join()

        print('OK')
        print(ERROR_LIST)
        with open('error_list.py', 'w+') as f:
            f.write(str(ERROR_LIST))

    # 爬完后会发现有 mid=[38, 35, 23, ......]的用户数据无法获取，需要进步不改善


if __name__ == '__main__':
    main()
