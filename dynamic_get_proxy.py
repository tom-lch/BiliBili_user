# 从https://www.xicidaili.com/nn/动态的获取IP
import urllib
from lxml import etree
import requests
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
}


# 从代理IP网站获取随机的ip
def get_ip_lists(url):
    text = requests.get(url=url, headers=headers).text
    tree = etree.HTML(text)
    ip_nodes = tree.xpath('//table[@id="ip_list"]//tr')[1:]
    ip_list = []
    # 从tr中获取ip和端口号
    for ip_node in ip_nodes:
        ip_list.append(ip_node.xpath('.//td[2]/text()')[0] + ':' + ip_node.xpath('.//td[3]/text()')[0])
    # 验证ip是否可用
    for ip in ip_list:
        try:
            url = 'https://' + ip
            temp = {'https': url}
            res = urllib.urlopen(url, proxies=temp).read()
        except Exception as e:
            # 不可用从列表中展删除
            ip_list.remove(ip)
            continue
    return ip_list


def get_random_ip():
    url = 'https://www.xicidaili.com/nn/'
    # 获取可用的IP池
    ip_list = get_ip_lists(url)
    # 从IP池中随机选一个ip返回
    ip = random.sample(ip_list, 1)[0]
    proxies = {'http': 'http://'+ip}
    return proxies

# if __name__ == '__main__':
#    main()
