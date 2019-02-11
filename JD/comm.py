
import re
import chardet
import configparser
import time
import json
from datetime import datetime,timedelta
import random

## 时间处理函数 放入comm.py中
def gettimenow(strftime = False):
	'''此处得到的世界都是东八区北京时间'''
	d8 = timedelta(hours = 8)
	if strftime:
		return (datetime.utcnow() + d8).strftime('%Y-%m-%d %H:%M:%S')
	else:
		return datetime.utcnow() + d8
        
def getHeaders(num = 1):
	result = []
	temp = []
	with open('headers.txt','r',encoding='utf-8') as f:
		temp = f.readlines()
	result = [i.strip() for i in temp if i.strip() !='']
	if len(result)>0:
		if len(result)<=num:
			return result
		else:
			return random.sample(result,num)
	else:
		return []

if __name__ == "__main__":
	# test = reviews()
	# test.run()
	# crawl(keyword = keywordlist[0])
	# print(gettimenow(strftime=True))
	result = getHeaders()
	for res in result:
		print(res)
	print(len(result))
	pass