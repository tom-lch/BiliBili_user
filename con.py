a = '__jp4({"code":0,"message":"0","ttl":1,"data":{"mid":16061199,"following":825,"whisper":0,"black":0,"follower":41635}})'

import re

b = re.match('^f+', a)

print(b)
