import requests
from lxml import etree
import re
import urllib3
import chardet
import configparser
import time
import json
from datetime import datetime,timedelta
from jd import reviews

from multiprocessing.pool import ThreadPool

# 获取config
config = configparser.RawConfigParser()
config.read('config.txt',encoding="utf-8")

#数据库
import redis
dbredis = redis.Redis(host='10.41.75.56',port=6379)
startnumber = dbredis.scard('Reviews_norepeat6')

# 此处针对所有的网商,需要继续修改，暂时只针对京东JD
goodsnamelist = ['Dell','HP','Lenovo','ViewSonic',]   # 这个值还要获取
goodstypelist = []
# for goodsname in goodsnamelist:
	# keywords= config.get('JD-' +goodsname,'keywords')
	# client = config.get('amazon-' +goodsname,'Account')
	# keywordlist = keywords.split('/')
	# templist = [(goodsname,i,client) for i in keywordlist]
	# goodstypelist.extend(templist)



def crawl(goodsname,keyword,client):
	# 此接口爬取全站
	print('爬取%s的数据开始...' %keyword)
	reviews(goodsname=goodsname,keyword = keyword,client = client).run()
	print('爬取%s的数据结束' %keyword)
		
def crawl_update():
	#此接口只更新数据
	pass
	
# 线程处理


numofprocess = 10 # 此处由config控制，未写完

pool = ThreadPool(numofprocess)
for i in range(numofprocess):
	temp = reviews(tag=i+1)
	pool.apply(func = temp.consumer)
pool.close()
pool.join()

endnumber = dbredis.scard('Reviews_norepeat6')

print('update JD {} records'.format(endnumber-startnumber))

if __name__ == "__main__":
	# for i in goodstypelist:
		# print(i)
	pass