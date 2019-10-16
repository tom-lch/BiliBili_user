a = '__jp4({"code":0,"message":"0","ttl":1,"data":{"mid":16061199,"following":825,"whisper":0,"black":0,"follower":41635}})'
#方法一：使用正则提取关注和粉丝量
import re

b = re.match('^f+', a)

print(b)
#方法二：
b = a[6:-1]
