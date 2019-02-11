import requests
from requests.utils import cookiejar_from_dict,dict_from_cookiejar
from lxml import etree
import re
import urllib3
import chardet
import configparser
import time
import random
from datetime import datetime,timedelta
from pyquery import PyQuery as pq
import hashlib
import json
from Proxy import get_one_proxy
import os

#import redis
import random

keywords_temp = 'P2217/P2317H/P2418HT/P2717H/S2418H/S2418HN/S2718D/S2817Q/U2417H/U2717D/U2917W/UP3017/UP3218K/C5518QT/C8618QT/UP2718Q/U2518D/U2518DR/P2319H/P2719H/S2419HM/S2719DM/P2719HC/S2319HS/S2719HS/S2719DC/U2419H/U2419HC/U2719D/U2719DC/U2719DX'.split('/')
keywords_type = {}

for k in keywords_temp:
	keywords_type[k] = 'Dell'
## 解析下载页面
class reviews(object):
	def __init__(self,goodsname='Dell',keyword='P2317H',client='Rosa',tag = None,startpage=1):
		self.startpage = startpage
		self.tag = tag
		#self.dbmysql = MysqlPipeline()
		self.client = client
		self.goodsname = goodsname
		self.max_record_per_file = 5000 #一个文件保存5000条数据
		self.record_file_num = 1 #文件
		self.record_num = 0 # 文件内部记录计数
		self.results = [] #临时存放记录
		self.last_md5 = '' #上一条记录的md5 初步去重使用
		self.timeout = 30
		self.count = 0
		self.goodid_list = []
		self.keyword = self.goodsname + ' ' +keyword
		self.session2 = requests.session()
		self.headers = {
				'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
			}
		
		self.proxy = {
			'http':'10.32.33.252:8080',
			'https':'10.32.33.252:8080'
			}
		self.session = requests.session()
		self.cookies_dict = []
		cookies = {
						'_cc_':'UIHiLt3xSw%3D%3D',
						'_m_h5_tk':'10471a57941eef7432c665fea7fc6c8e_1543374150035',
						'_m_h5_tk_enc':'5fae6692452b297292f736fcad435eb3',
						'_tb_token_':'e0354eb3497b5',
						'cna':'urphFA2+QgcCAT3czp0RFlrD',
						'cookie2':'1d9b767e99475102b156ab9aa57edabb',
						'enc':'7iAF8umdM6oSOiaYUqOo3aRq09KG%2BScT%2BMhP1cLsUyb1pfhHnINjlCTj9u6dOm1JJwVsYTbKw5j3v0mYVOxXsw%3D%3D',
						'hng':'CN%7Czh-CN%7CCNY%7C156',
						'isg':'BA8PW2tAiPir54wH83u4X1CTnqMTHafomWpkISEcJH6F8C7yKAbFpgDq9ijOiDvO',
						'l':'AsnJISPOmSAhjuYKIeBuHb0-Wf4jrL1P',
						'lgc':'luomoxingkong',
						'mt':'ci=1_1',
						't':'cfcbdf6c5e7e70ec61e509b3e893cacc',
						'tg':'0',
						'thw':'cn',
						'tracknick':'luomoxingkong',
						'uc1':'cookie14=UoTYNciNHpUWUA%3D%3D',
						'uc3':'vt3=F8dByR6lf5c4OMpYbUo%3D&id2=VWwxtcDqayt2&nk2=D9ZMK7Ev282mNQN0Uw%3D%3D&lg2=WqG3DMC9VAQiUQ%3D%3D',
						'v':'0',
						'x':'e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0',
		}
		self.cookies_dict.append(cookiejar_from_dict(cookies))
		
		cookies_dict2 = {
				'_cc_':'W5iHLLyFfA%3D%3D',
				'_m_h5_tk':'a5ab5dfcb55727a6fda16133b6919bbd_1539592530258',
				'_m_h5_tk_enc':'55e3ea79827c2b28b8273866752948b0',
				'_tb_token_':'3e381e930e877',
				'cna':'0wIyFPE16hECAQopRSm97eOn',
				'cookie2':'28890cec51fbe3d018474376e72a06b3',
				'enc':'UvlnakXVddg%2FddYKSxfGSHGMMR7wBIcCSaNjAl1N%2FQLhHDp9gLRLtdLRAOR6ag7CXM5P%2FbdjwzDsdUWjQsPdKg%3D%3D',
				'hng':'CN%7Czh-CN%7CCNY%7C156',
				'isg':'Al9fYi86eNKJNXzOylkleVP87rOpGbNmOFnIYvGs8I5VgH8C-ZRDtt1QNKYC',
				'l':'ApeXuTOaw50Ueqojpsx40ok1pwDh12s-',
				'lgc':'karta282950',
				'mt':'ci=60_1',
				't':'4fcc0e67d2fbe3b7f39e5b0a122f9b6c',
				'tg':'0',
				'thw':'cn',
				'tracknick':'karta282950',
				'uc1':'cookie14=UoTfItXVxHrj9w%3D%3D&lng=zh_CN&cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D&existShop=false&cookie21=W5iHLLyFe3xm&tag=8&cookie15=UIHiLt3xD8xYTw%3D%3D&pas=0',
				'uc3':'vt3=F8dByRmuKStFqcR3p%2F0%3D&id2=UNaA0B59uXjffQ%3D%3D&nk2=CNam5rl%2Fp0QVf8E%3D&lg2=UIHiLt3xD8xYTw%3D%3D',
				'unb':'3670165215',
				'v':'0',
				'x':'e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0',
		}
		self.cookies_dict.append(cookiejar_from_dict(cookies_dict2))
		cookies_dict3 = {
			'JSESSIONID':'48D5400F0AE06DAD5D7FE4AA8AD33355',
			'_cc_':'W5iHLLyFfA%3D%3D',
			'_fbp':'fb.1.1543392611349.141299794',
			'_l_g_':'Ug%3D%3D',
			'_m_h5_tk':'cb04d72d4bcecbfd1c4e09deee63852c_1543402319007',
			'_m_h5_tk_enc':'08aa26bb0ac1787ac52b94defc15751f',
			'_nk_':'jonny_test1',
			'_tb_token_':'e0354eb3497b5',
			'cna':'urphFA2+QgcCAT3czp0RFlrD',
			'cookie1':'BYFXB3fZHWy%2Bah%2FlvJ83pW6JHZ62IjOH8Z5rKFK%2Bmck%3D',
			'cookie17':'UoLfdCnbIqFUtP%2BN',
			'cookie2':'1d9b767e99475102b156ab9aa57edabb',
			'csg':'aebf51f0',
			'dnk':'jonny_test1',
			'enc':'fOXs6%2F0jgMijH20Ey84w1SYlJeYzL%2FSUecfodHxgbU66C%2FsyquZTfwoWg4GVeJLZf%2Ba21RhFXW%2FtZJUTTNM3ow%3D%3D',
			'existShop':'MTU0MzM5NTQ1OQ%3D%3D',
			'hng':'GLOBAL%7Czh-CN%7CUSD%7C999',
			'isg':'BObmTCUogY90wlUrWJ5pfKEYN1xi7u4_mOldjtCP8Yn9U4ZtOVXykbIhrwf6eyKZ',
			'l':'Ary8zxaipBckfcDxRUaj6WLSDFFubWDe',
			'lgc':'jonny_test1',
			'mt':'ci=0_1',
			'sg':'151',
			'skt':'ec56c4ef45378735',
			'swfstore':'281840',
			't':'cfcbdf6c5e7e70ec61e509b3e893cacc',
			'tg':'5',
			'thw':'cn',
			'tracknick':'jonny_test1',
			'uc1':'cookie16=WqG3DMC9UpAPBHGz5QBErFxlCA%3D%3D&cookie21=V32FPkk%2FgihF%2FS5nqH3j&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&pas=0&cookie14=UoTYNciNG1JGVw%3D%3D&tag=8&lng=zh_CN',
			'uc3':'vt3=F8dByR6lcmW6sgI5foc%3D&id2=UoLfdCnbIqFUtP%2BN&nk2=CdzyrrmtfW3pTfw%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D',
			'unb':'133446795745',
			'v':'0',
			'whl':'-1%260%260%261543395515976',
			'x':'e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0',
		}
		self.cookies_dict.append(cookiejar_from_dict(cookies_dict3))
		self.cookies_dict4 = {
			'cc_':'VT5L2FSpdA%3D%3D',
			'_fbp':'fb.1.1543554930230.588326534',
			'_l_g_':'Ug%3D%3D',
			'_m_h5_tk':'8c7e86aed94f3c9b738e64328807ed17_1543563926745',
			'_m_h5_tk_enc':'14095df0dcae827d9cfd269c5164a68b',
			'_nk_':'jonny_test2',
			'_tb_token_':'ea35b8357efee',
			'cna':'urphFA2+QgcCAT3czp0RFlrD',
			'cookie1':'U%2BWsEOeW5P0dOCjRR0CEN6YE5Ipvzr6pbmuxUl31Y5M%3D',
			'cookie17':'UoLfdCnbLCAT44Ec',
			'cookie2':'113920572337d78635cbebb3359d6582',
			'csg':'256ab252',
			'dnk':'jonny_test2',
			'enc':'fOXs6%2F0jgMijH20Ey84w1SYlJeYzL%2FSUecfodHxgbU66C%2FsyquZTfwoWg4GVeJLZf%2Ba21RhFXW%2FtZJUTTNM3ow%3D%3D',
			'existShop':'MTU0MzU1NTA0Nw%3D%3D',
			'hng':'GLOBAL%7Czh-CN%7CUSD%7C999',
			'isg':'BI2N1o_I7Wx8pElA-BoXTRrVnKkNQwWCL3wme88SySSTxq14l7rRDNtUNBIFBtn0',
			'l':'ArGxaHFTIRiJ9t22AB3BqMCCQTZLHSUQ',
			'lgc':'jonny_test2',
			'mt':'ci=0_1',
			'sg':'295',
			'skt':'8ef906a9e5a03225',
			't':'cfcbdf6c5e7e70ec61e509b3e893cacc',
			'tg':'5',
			'thw':'cn',
			'tracknick':'jonny_test2',
			'uc1':'cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D&cookie21=UtASsssmeW6lpyd%2BAHnb&cookie15=VFC%2FuZ9ayeYq2g%3D%3D&existShop=false&pas=0&cookie14=UoTYNc5xYp2%2FKA%3D%3D&tag=8&lng=zh_CN',
			'uc3':'vt3=F8dByR1X72ADMXhXRrs%3D&id2=UoLfdCnbLCAT44Ec&nk2=CdzyrrmtfW3pTf8%3D&lg2=VFC%2FuZ9ayeYq2g%3D%3D',
			'unb':'133446962679',
			'v':'0',
			'x':'e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0',
		}
		self.cookies_dict.append(cookiejar_from_dict(self.cookies_dict4))
		self.cookie_id = 0
		self.page = startpage
		self.session.cookies = random.choice(self.cookies_dict)
		self.sessionlist = []
		for cook in self.cookies_dict:
			tempsession = requests.session()
			tempsession.cookies = cook
			self.sessionlist.append(tempsession)
		self.keyword2 = keyword #用来匹配
		self.pattern = r'\/(\d+?)\.html' #从url中获取goodid
		
		# 用来去掉已经爬过了的店铺
		self.setfilter = set()
	
		self.lock = True
		self.switch = True # 当分页处理完成，设置为False
		self.comment_switch = {}# 评论分页开关,键名为goodid
		
		# 测试
		self.test = []
		
		# self.session.get('https://world.taobao.com/',headers=self.headers,proxies = self.proxy)
				
	def parse_comment(self,goodid,callback = None,meta=None,keyword=None,goodsname=None,client=None):
		i =1
		if callback is None:
			callback = self.comment_detail
		self.count = 0
		print('正在获取好评')
		url = '''https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum=1&pageSize=20&rateType=1&orderType=feedbackdate&attribute=&sku=&hasSku=false&folded=0&_ksTS={}&callback=jsonp_tbcrate_reviews_list'''.format(goodid,"{}".format(time.time()*1000).replace('.','_'))
		callback( goodid = goodid, url = url ,page = i, callback = self.comment_detail,meta=meta,keyword=keyword,goodsname=goodsname,client=client,default=5) #好评五分
		self.count = 0
		print('正在获取中评')
		url = '''https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum=1&pageSize=20&rateType=0&orderType=feedbackdate&attribute=&sku=&hasSku=false&folded=0&_ksTS={}&callback=jsonp_tbcrate_reviews_list'''.format(goodid,"{}".format(time.time()*1000).replace('.','_'))
		callback( goodid = goodid, url = url,page = i, callback = self.comment_detail,meta=meta,keyword=keyword,goodsname=goodsname,client=client,default=3) #中评三分
		self.count = 0
		print('正在获取差评')
		url = '''https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum=1&pageSize=20&rateType=-1&orderType=feedbackdate&attribute=&sku=&hasSku=false&folded=0&_ksTS={}&callback=jsonp_tbcrate_reviews_list'''.format(goodid,"{}".format(time.time()*1000).replace('.','_'))
		callback( goodid = goodid, url = url, page = i, callback = self.comment_detail,meta=meta,keyword=keyword,goodsname=goodsname,client=client,default=1) #差评一分
				
	def comment_detail(self,goodid,url = None,page = 1,callback=None,meta=None,keyword=None,goodsname=None,client=None,default=None):
		self.session = random.choice(self.sessionlist)
		print('Page {}'.format(page))
		# 解析详情页，获取评论信息
		if callback is None:
			callback = self.comment_detail
		if page == 0:
			url = self.get_cookies(goodid)
			print(url)
		else:
			if url is None:
				url = '''https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum=1&pageSize=20&rateType=1&orderType=feedbackdate&attribute=&sku=&hasSku=false&folded=0&_ksTS={}&callback=jsonp_tbcrate_reviews_list'''.format(goodid,"{}".format(time.time()*1000).replace('.','_'))
			url = re.sub(r'&currentPageNum=(\d+?)&','&currentPageNum={}&'.format(page),url)
			
			url = re.sub(r'&_ksTS=[\d_]+?&','&currentPageNum={}&'.format("{}".format(time.time()*1000).replace('.','_')),url)
		print(url)
		try:
			headers = {'User-Agent':self.get_headers()}
			temp_proxy = get_one_proxy()
			#proxies = {'http':'122.116.144.41:55160','https':'122.116.144.41:55160'}
			proxies = {'http':temp_proxy.strip(),'https':temp_proxy.strip()}
			resp = requests.get(url,headers=headers,proxies = proxies,timeout = self.timeout)
		except Exception as e:
			print(e)
			callback(goodid,url=url,page = page,callback=callback,meta=meta,keyword=keyword,goodsname=goodsname,client=client,default=default)
			# logging.error('Fatal error:'+url+'downloaded fail')
			return
		cod = resp.encoding
		result = resp.content.decode(cod)
		# print(result)
		reT = r'\w+?\((.*?)\)$'
		res = re.search(reT,result,re.S)
		if res:
			res = res.group(1)
			res = json.loads(res)
			try:
				comments = res.get("comments",[])
			except Exception as e:
				# logging.error('comment_detail error:' + e)
				return
				
			print(self.count,len(comments))
			if len(comments) == 0:
				if self.count >=5:
					self.comment_switch[goodid] = False
					return
				if callback is None:
					callback = self.comment_detail
				self.count += 1
				print(self.count)
				callback(goodid,url=url,page = page,callback=callback,meta=meta,keyword=keyword,goodsname=goodsname,client=client,default=default)
				return
				#self.comment_switch[goodid] = False
		
			myresult = []# 最终要获得的数据 结构
			self.count = 0
			temp2 = {}
			for i in comments:
				# print(i)
				# print('#'*50)
				temp = {}
				temp['crawltime'] = datetime.utcnow().strftime('%Y-%m-%d')
				temp['size'] = i.get('productSize',None)
				temp['comment_time'] = i.get('date',None) # 2018年11月22日 15:23
				temp['content'] = i.get('content','')# 这个当然不错的了，我们是用来作图的
				temp['img'] = i.get('photos')
				temp['img'] = json.dumps(list(map(lambda x:re.sub(r'^(https:)?//','https://',x.get('url','')).replace('_400x400.jpg',''),temp.get('img',[]))))
				if len(temp['img']) == 0:
					temp['img'] = None
				temp['content'] = i.get('content')
				# print(temp['website_url'])
				temp['website'] = 'JD'
				temp['website_url'] = 'http://www.jd.com'
				#http://img30.360buyimg.com/shaidan/jfs/t23899/69/1404782488/83204/3b210e9c/5b5ef8f1N3d24d6b6.jpg
				temp['type'] = self.keyword if keyword is None else keyword
				temp['client'] = self.client if client is None else client
				temp['score'] = i.get('score',default)
				replies = i.get('replies',None)
				temp['replytime'] = i.get('shareInfo',{}).get('lastReplyTime','')
				if temp['replytime'] == '':
					temp['replytime'] = None
					
				temp['md5_id'] = self.md5('{}{}'.format(goodid,i.get('rateId','')))
				temp['goodsname'] = self.goodsname if goodsname is None else goodsname
				norepeat = self.md5('{}{}{}'.format(goodid,i.get('rateId',''),temp['replytime'] if temp['replytime'] else 'null'))
				print(temp)
				self.results.append(temp)
				self.record_num += 1
				if self.record_num >= self.max_record_per_file:
					self.save_to_file()
			
			# md5_temp = self.md5(temp)			
			# if md5_temp == self.last_md5 and len(temp)>0:
				# return
			# else:
				# self.last_md5 = md5_temp

			page = page +1
			if callback is None:
				callback = self.comment_detail
			callback(goodid,url=url,page = page,callback=callback,meta=meta,keyword=keyword,goodsname=goodsname,client=client,default=default)
			return
		
	def md5(self,rawString):
		if not isinstance(rawString,str):
			return
		s = hashlib.md5(rawString.encode())
		return s.hexdigest()
		
			
	def download_dell_TMall(self,url=None,callback=None):
		if callback is None:
			callback = self.dell_store
		if url is None and self.page==0:
			url = 'https://s.taobao.com/search?spm=a230r.1.1998181369.d4919860.2e9f1fcfzMnVGu&q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&js=1&initiative_id=staobaoz_20181128&ie=utf8&bcoffset=-9&ntoffset=-9&p4ppushleft=%2C44&tab=mall&cps=yes&ppath=20000%3A26683'
		if url is None and self.page!=0:
			url = 'https://s.taobao.com/search?spm=a230r.1.1998181369.d4919860.2e9f1fcfzMnVGu&q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&js=1&initiative_id=staobaoz_20181128&ie=utf8&bcoffset=-9&ntoffset=-9&p4ppushleft=%2C44&tab=mall&cps=yes&ppath=20000%3A26683'
			url = re.sub(r'&s=(\d+?)$','',url)
			url += '&s={}'.format(self.page*44)
		rawurl = url
		resp = requests.get(url,headers=self.headers,proxies=self.proxy)
		# print(resp.url)
		result = resp.text
		# print(result)
		result = re.search(r'g_page_config = ({.*?});',result,re.S)
		# print(self.session.cookies)
		if result:
			result = json.loads(result.group(1))
			items = result.get('mods',{}).get('itemlist',{}).get('data',{}).get('auctions',[])
			print(len(items))
			for item in items:
				shopname = item.get('nick')
				price = item.get('view_price')
				url = item.get('detail_url')
				title = item.get('raw_title')
				goodid = re.findall(r'\?id=(\d+?)&',url)
				if goodid:
					goodid = goodid[0]
				else:
					continue
				if '差价' in title:
					continue
				if '英寸' not in title:
					continue
				type = None
				for i in keywords_type.keys():
					if i in title:
						type = i
						break
				print(type)
				if type is None:
					continue
				# dbredis.sadd('TMall_goodid',(goodid,type))
				print(shopname,price,goodid,title)
			# 处理分页
			if self.page >= 50 or len(items) <44:
				return
			self.page += 1
			url = rawurl
			url = re.sub(r'&s=(\d+?)$','',url)
			url += '&s={}'.format(self.page*44)
			if url.startswith('//'):
				url = 'https:'+url
				print(url)
			self.download_dell_TMall(url)
		# else:
			# print('正在更换用户...')
			# self.cookie_id = self.cookie_id + 1 if self.cookie_id + 1 <len(self.cookies_dict) else 0
			# self.session.cookies = self.cookies_dict[self.cookie_id]
			# self.download_dell_TMall(url=url,callback=callback)
		# callback(resp.text)
		print('天猫导入完成,共导入{}条数据'.format(self.page))
	
	def download_dell_Taobao(self,url=None,callback=None):
		self.session.cookies = random.choice(self.cookies_dict)
		if callback is None:
			callback = self.parse_comment
		if url is None and self.page==0:
			url = 'https://s.taobao.com/search?spm=a230r.1.1998181369.d4919860.2e9f1fcfzMnVGu&q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&js=1&initiative_id=staobaoz_20181128&ie=utf8&bcoffset=-9&ntoffset=-9&p4ppushleft=%2C44&tab=mall&cps=yes&ppath=20000%3A26683'
		if url is None and self.page!=0:
			url = 'https://s.taobao.com/search?spm=a230r.1.1998181369.d4919860.2e9f1fcfzMnVGu&q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&js=1&initiative_id=staobaoz_20181128&ie=utf8&bcoffset=-9&ntoffset=-9&p4ppushleft=%2C44&tab=mall&cps=yes&ppath=20000%3A26683'
			url = re.sub(r'&s=(\d+?)$','',url)
			url += '&s={}'.format(self.page*44)
		rawurl = url
		if self.count >=10:
			time.sleep(300)
			self.count = 0
		headers = {'User-Agent':self.get_headers()}
		headers['cookie'] = 'cna=urphFA2+QgcCAT3czp0RFlrD; t=cfcbdf6c5e7e70ec61e509b3e893cacc; _cc_=URm48syIZQ%3D%3D; tg=0; l=AsvLG1l6sk/iMXekLpNLMpmk22S10t/i; enc=ddv2AfS73bAhE5TaTHRE7lY%2FsnloFft7cUqDn%2B6k1ekOfrN4duFionnjGCyhEpz%2FnRl9%2FHuS6ZucHRurQ8drjA%3D%3D; _uab_collina=154407940266705370937115; thw=tw; hng=TW%7Czh-TW%7CTWD%7C158; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; _m_h5_tk=12c6025833330a8057cc7fbdbdb899c7_1544151605085; _m_h5_tk_enc=6e833b2b8360d85dea0e2cbd677b44a6; cookie2=142aa50b21624f6dc0cde7974b608e1b; _tb_token_=7ee603780db1b; _fbp=fb.1.1544142611079.761093547; alitrackid=world.taobao.com; lastalitrackid=world.taobao.com; swfstore=245366; v=0; uc1=cookie14=UoTYMh9%2BrwN37g%3D%3D; mt=ci=-1_0; x5sec=7b227365617263686170703b32223a223738376530653737386530633432306535646261613233306164353835633933434f697a702b4146454b2f6673726a71355a50346a674561437a597a4d5463314d6a51314f547379227d; JSESSIONID=3EDBD25CB01DC1E8AF7FF2B28F4B38E8; isg=BOnp0iHokRFsr62sPFb7mWah-JVJnxmQI0gCF4vYjlOSUh5k0Qd4uLcEEL5BSnUg'
		temp_proxy = get_one_proxy()
		#proxies = {'http':'122.116.144.41:55160','https':'122.116.144.41:55160'}
		proxies = {'http':temp_proxy.strip(),'https':temp_proxy.strip()}
		try:
			resp = self.session2.get(url,headers=headers,proxies=proxies,timeout = self.timeout)
		except Exception as e :
			print(e)
			return self.download_dell_Taobao(url=url,callback=callback)
		# print(resp.url)
		result = resp.text
		# print(result)
		result = re.search(r'g_page_config = ({.*?});',result,re.S)
		# print(self.session.cookies)
		if result:
			self.count = 0
			result = json.loads(result.group(1))
			items = result.get('mods',{}).get('itemlist',{}).get('data',{}).get('auctions',[])
			print(len(items))
			for item in items:
				shopname = item.get('nick')
				price = item.get('view_price')
				url = item.get('detail_url')
				title = item.get('raw_title')
				goodid = re.findall(r'\?id=(\d+?)&',url)
				if goodid:
					goodid = goodid[0]
				else:
					continue
				if '差价' in title:
					continue
				if '英寸' not in title:
					continue
				type = None
				for i in keywords_type.keys():
					if i in title:
						type = i
						break
				# print(type)
				if type is None:
					continue
				websites = item.get('icon',[])
				for website in websites:
					if '尚天猫，就购了' in website.get('title',''):
						print(website.get('title',''))
						continue
				# dbredis.sadd('TMall_goodid',(goodid,type))
				print(shopname,price,goodid,title,type,sep='\n')
				self.goodid_list.append((shopname,price,goodid,title,type))
			# 处理分页
			if self.page < self.startpage+5 and len(items) ==44:
				self.page += 1
				url = rawurl
				url = re.sub(r'&s=(\d+?)$','',url)
				url += '&s={}'.format(self.page*44)
				print('url:{}'.format(url))
				if url.startswith('//'):
					url = 'https:'+url
					print(url)
				return self.download_dell_Taobao(url) # 下载分页
		else:
			print('正在更换用户...')
			time.sleep(30)
			self.count += 1
			self.cookie_id = self.cookie_id + 1 if self.cookie_id + 1 <len(self.cookies_dict) else 0
			self.session.cookies = self.cookies_dict[self.cookie_id]
			return self.download_dell_Taobao(url=url,callback=callback)
		print('淘宝导入完成,共导入{}条数据'.format(self.page))
		with open('goodid{}.txt'.format(self.startpage),'w') as f:
			f.write(json.dumps(self.goodid_list))
		print('数据写入完成...')
			
	def get_headers(self):
		with open('headers.txt','r') as f:
			result_list = f.readlines()
		result_list = filter(lambda x:x.strip(),result_list)
		return random.choice(list(result_list)).strip()
	def save_to_file(self):
		if not os.path.exists('data') or not os.path.isdir('data'):
			os.mkdir('data')
		filename = 'data_{}_{}'.format(self.tag,self.record_file_num)
		with open('data/'+filename,'a') as f:
			for result in self.results:
				f.write(json.dumps(result)+'\n')
		self.record_num = 0
		self.record_file_num += 1
		self.results.clear() # 清空临时存储
        
	def testD(self):
		url = 'https://s.taobao.com/search'
		data = {
			'data-key':'s',
			'data-value':'264',
			'ajax':'true',
			'_ksTS': "{}".format(time.time()*1000).replace('.','_'),
			'callback':'jsonp{}'.format("{}".format(time.time()*1000).replace('.','_').split('_')[1]),
			'q':'显示器',
			'imgfile':'', 
			'js':'1',
			'stats_click':'search_radio_all:1',
			'initiative_id':'staobaoz_20181207',
			'ie':'utf8',
			'cps':'yes',
			'ppath':'20000:26683',
			'bcoffset':'3',
			'ntoffset':'3',
			'p4ppushleft':'1,48',
			's':'44',
		}
		headers = {'User-Agent':self.get_headers()}
		temp_proxy = get_one_proxy()
		proxies = {'http':temp_proxy.strip(),'https':temp_proxy.strip()}
		headers['cookie'] = 'cna=urphFA2+QgcCAT3czp0RFlrD; t=cfcbdf6c5e7e70ec61e509b3e893cacc; _cc_=URm48syIZQ%3D%3D; tg=0; l=AsvLG1l6sk/iMXekLpNLMpmk22S10t/i; enc=ddv2AfS73bAhE5TaTHRE7lY%2FsnloFft7cUqDn%2B6k1ekOfrN4duFionnjGCyhEpz%2FnRl9%2FHuS6ZucHRurQ8drjA%3D%3D; _uab_collina=154407940266705370937115; thw=tw; hng=TW%7Czh-TW%7CTWD%7C158; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; _m_h5_tk=12c6025833330a8057cc7fbdbdb899c7_1544151605085; _m_h5_tk_enc=6e833b2b8360d85dea0e2cbd677b44a6; cookie2=142aa50b21624f6dc0cde7974b608e1b; _tb_token_=7ee603780db1b; _fbp=fb.1.1544142611079.761093547; alitrackid=world.taobao.com; lastalitrackid=world.taobao.com; swfstore=245366; v=0; uc1=cookie14=UoTYMh9%2BrwN37g%3D%3D; mt=ci=-1_0; x5sec=7b227365617263686170703b32223a223738376530653737386530633432306535646261613233306164353835633933434f697a702b4146454b2f6673726a71355a50346a674561437a597a4d5463314d6a51314f547379227d; JSESSIONID=4E59B8904FEDB78C25510C048E50018B; isg=BDc3yuOiJwcPVKOCvsxtL0TLxiuL1c8mgTKMuYnhYoSGOER6k86erp5eHtDD0OPW'
		# headers['referer']='https://s.taobao.com/search?q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20181207&ie=utf8&cps=yes&ppath=20000%3A26683&bcoffset=3&ntoffset=3&p4ppushleft=1%2C48&s=44'
		resp = requests.get(url,params=data,headers=headers,proxies=proxies)
		# print(resp.url)
		result = resp.text
		print(result)
		return 
		

			
if __name__ == "__main__":
	test = reviews(startpage=15)
	# url = 'https://s.taobao.com/search?spm=a230r.1.1998181369.d4919860.2e9f1fcfzMnVGu&q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&js=1&initiative_id=staobaoz_20181128&ie=utf8&bcoffset=-9&ntoffset=-9&p4ppushleft=%2C44&tab=mall&cps=yes&ppath=20000%3A26683'
	# test.download_dell_TMall(url)
	# url = 'https://s.taobao.com/search?spm=a230r.1.1998181369.1.28de1fcf3KIiL1&q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&js=1&initiative_id=staobaoz_20181128&ie=utf8&bcoffset=-9&ntoffset=-9&p4ppushleft=%2C44&tab=all&cps=yes&ppath=20000%3A26683'
	# test.download_dell_Taobao(url)

	# url = test.get_cookies('574181045914')
	# test.comment_detail('562824950448')
	# test.parse_comment('582259981056')
	# headers = test.get_headers()
	# print(headers)
	# test.get_cookies2('566848769176')
	# test.save_to_file()
	test.download_dell_Taobao()
	# test.testD()
