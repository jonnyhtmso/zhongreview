import requests
from lxml import etree
import re
import urllib3
import chardet
import configparser
import time
import json
from datetime import datetime,timedelta

from pyquery import PyQuery as pq

from pipelines3 import MongodbPipeline,MysqlPipeline

import hashlib

from comm import gettimenow

from loglib import logging

import redis

dbredis = redis.Redis(host="10.41.75.56",port=6379,db=2)

# 获取config
config = configparser.RawConfigParser()
config.read('config.txt',encoding="utf-8")

keywords= config.get('JD-Dell','keywords')
keywordlist = ['Dell ' + i for i  in  keywords.split('/')]



# logging.error(__file__ + ' '+ __name__ + ': get a error! ----- test')
keywords_Dell = 'P2217/P2317H/P2418HT/P2717H/S2418H/S2418HN/S2718D/S2817Q/U2417H/U2717D/U2917W/UP3017/UP3218K/C5518QT/C8618QT/UP2718Q/U2518D/U2518DR/P2319H/P2719H/S2419HM/S2719DM/P2719HC/S2319HS/S2719HS/S2719DC/U2419H/U2419HC/U2719D/U2719DC/U2719DX'.split('/')
keywords_HP  = 'Pavillion27q/27q/S340c/Envy 34/Z27/Z32/Z43/V220'.split('/')
keywords_Lenovo = 'T2324C/P24i-1/T24i-10/T24m-10/L20-10/P32u-10/T2054pc/T2254pc/LT2423wc'.split('/')
keywords_ViewSonic = 'VP2468/VP2768/VP3881/VP2771/VP2785/VG2448/TD2220/TD2420/VX2778-SMHD'.split('/')

keywords_type = {} # keywords 商品字典
for k in keywords_Dell:
	keywords_type[k] = 'Dell'
for k in keywords_HP:
	keywords_type[k] = 'HP'
for k in keywords_Lenovo:
	keywords_type[k] = 'Lenovo'
for k in keywords_ViewSonic:
	keywords_type[k] = 'ViewSonic'

customer_goods = {'Dell':'Rosa','HP':'Astro','Lenovo':'Lily','ViewSonic':'Rainbow'}

keyword_list = []
keyword_list.extend(keywords_Dell)
keyword_list.extend(keywords_HP)
keyword_list.extend(keywords_Lenovo)
keyword_list.extend(keywords_ViewSonic)

dell_url = 'http://list.jd.com/list.html?cat=670,677,688&ev=exbrand_5821&sort=sort_commentcount_desc&trans=1&JL=3_%E5%93%81%E7%89%8C_%E6%88%B4%E5%B0%94%EF%BC%88DELL%EF%BC%89#J_crumbsBar'
hp_url = 'http://list.jd.com/list.html?cat=670,677,688&ev=exbrand_8740&sort=sort_commentcount_desc&trans=1&JL=3_%E5%93%81%E7%89%8C_%E6%83%A0%E6%99%AE%EF%BC%88HP%EF%BC%89#J_crumbsBar'
lenovo_url = 'http://list.jd.com/list.html?cat=670,677,688&sort=sort_commentcount_desc&trans=1&ev=exbrand_11516&JL=3_%E5%93%81%E7%89%8C_%E8%81%94%E6%83%B3%EF%BC%88Lenovo%EF%BC%89#J_crumbsBar'
ViewSonic_url = 'http://list.jd.com/list.html?cat=670,677,688&ev=exbrand_20095&sort=sort_commentcount_desc&trans=1&JL=3_%E5%93%81%E7%89%8C_%E4%BC%98%E6%B4%BE%EF%BC%88ViewSonic%EF%BC%89#J_crumbsBar'

url_list = [dell_url,hp_url,lenovo_url,ViewSonic_url]
goods_list = ['Dell','HP','Lenovo','ViewSonic']
customer_keyword_list = [keywords_Dell,keywords_HP,keywords_Lenovo,keywords_ViewSonic]

## 解析下载页面
class reviews(object):
	def __init__(self,goodsname='Dell',keyword='P2317H',client='Rosa',tag = None,debug=False):
		self.debug = debug
		self.tag = tag
		self.dbmysql = MysqlPipeline()
		self.client = client
		self.goodsname = goodsname
		self.keyword = self.goodsname + ' ' +keyword
		self.headers = {
				'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
			}
		self.baseurl = 'https://search.jd.com'
		self.baseurl2 = 'http://item.jd.com'
		self.searchurl = 'http://search.jd.com/Search'
		self.prefix1 = 'Summary_' 
		self.prefix2 = 'Main_' #第一层json的值
		
		self.proxy = {
			'http':'10.41.65.25:1080',
			'https':'10.41.65.25:1080'
			}
		self.keyword2 = keyword #用来匹配
		self.pattern = r'\/(\d+?)\.html' #从url中获取goodid
		self.urlmoduel = 'https://item.jd.com/{}.html'
		
		# 用来去掉已经爬过了的店铺
		self.setfilter = set()
	
		
		data = {
			'keyword':self.keyword,
			'enc':'utf-8',
			'wq':self.keyword,
			'pvid':'7e5dd963f7084c468d817cf06a3351dc'
			}
		# print(data)
		self.lock = True
		try:
			resp = requests.get(self.searchurl,params=data,headers=self.headers,proxies = self.proxy)
			if '汪~没有找到' in resp.content.decode():
				self.lock = False
			# print(resp.status_code)
		except Exception as e:
			print('Fatal error')
			logging.error('Fatal error:'+self.searchurl+'downloaded fail')
			self.refer = self.searchurl
		else:
			self.refer = resp.url
		
		self.switch = True # 当分页处理完成，设置为False
		self.comment_switch = {}# 评论分页开关,键名为goodid
		# print(self.refer)
		
		# 测试
		self.test = []
		
		# 更新 
		self.maxpage = 5 #更新状态,最多翻看5页评论。
		self.update_status = False #默认不开启更新状态
	def __download(self,url,data,method='get',callable=None):
		pass
		
	def __search(self,page=1,callback = None, meta = None):
		'''
		page:第多少个半页
		'''
		# 解析第一部分 第一部分和第二部分可以合并
		# 解析第二部分
		# 处理分页
		if page>=200:
			return
		refer = self.refer
		url2 = 'https://search.jd.com/s_new.php'
		headers ={}
		headers['Referer'] = refer
		headers.update(self.headers)
		data2 = {
		'keyword':self.keyword,
		'enc':'utf-8',
		'qrst':'1',
		'rt':'1',
		'stop':'1',
		'vt':'2',
		'wq':self.keyword,
		'page':page,
		's':(page-1)*30+1,
		'scrolling':'y',
		'log_id':time.time(),
		'tpl':'1_M',
		}
		# print('测试') #测试时候使
		try:
			resp = requests.get(url2,params=data2,headers=headers,proxies=self.proxy)
		except Exception as e:
			logging.error('Fatal error:'+url2+'downloaded fail')
			return
		# code = resp.encoding
		logging.info('status code : {}' .format(resp.status_code))
		# print(resp.status_code)
		result = resp.text
		# print(result)
		html = etree.HTML(result)
		items = html.xpath(r'//li[@class = "gl-item"]')
		length = len(items)
		if length ==0:
			self.switch = False
		for item in items:
			temp_url = item.xpath(r'.//div[@class="p-img"]/a/@href')
			# print(temp_url)
			if len(temp_url)>0:
				_ = re.findall(self.pattern,temp_url[0])
				if len(_)>0:	
					url = self.urlmoduel.format(_[0])
					goodid = _[0]
					# print(url)
				else:
					continue
					pass
			else:
				continue
				
			# 为了数据完整性，此处需要修改
			
			res = etree.tostring(item)
			cod = chardet.detect(res).get("encoding")
			res = res.decode(cod)
			# kw = self.keyword.split(' ')
			reT = self.keyword2 + '[a-zA-Z]'
			# print(reT)
			
			
			res = re.sub(r'<font.+?>','',res)
			res = re.sub(r'</font>','',res)
			tres = etree.HTML(res)
			tres = tres.xpath(r'//a/em/text()') # 获取标题
			if len(tres):
				res = tres[0]
			else:
				print('空')
				continue
				
			print(res)
			if re.search(reT,res,re.S):
				logging.info('Invalid Match ')
				# print(goodid,'x')
				continue
			if self.keyword2 not in res:
				continue
			if '显示器' not in res:
				continue
			else:
				logging.info('{}'.format(goodid))
				print(res)
				# print(reT)
				# print(goodid,'okay')
				# continue #测试的时候使用
				if goodid in self.setfilter: #去掉爬过了的网页
					continue
				else:
					self.setfilter.add(goodid)
					
				print(goodid) #测试
				callback(goodid=goodid,callback=self.comment_detail)
				
				'''break # 必须删除，调试的时候使用
				'''

				
	def parse_comment(self,goodid,callback = None,meta=None,keyword=None,goodsname=None,client=None):
		i =0
		if callback is None:
			callback = self.comment_detail
		while self.comment_switch.get(goodid,True):
			#self.comment_switch.get(goodid)默认值为True
			# print(goodid)
			logging.info('Fetching %s comments, Page %s,begin' %(goodid,i+1))
			callback( goodid = goodid, page = i, callback = self.comment_detail,meta=meta,keyword=keyword,goodsname=goodsname,client=client)
			logging.info('Fetching %s comments, Page %s,done' %(goodid,i+1))
			i += 1
			
			# 更新模式下，最多翻看self.maxpage页  
			if self.update_status and i >=self.maxpage:
				break
		pass
				
	def comment_detail(self,goodid,page=0,callback=None,meta=None,keyword=None,goodsname=None,client=None):
		if self.debug:
			return print(goodid,page,keyword,goodsname,client)
		# url = self.urlmoduel.format(goodid)
		#url = 'http://sclub.jd.com/comment/productPageComments.action'
		url = 'http://club.jd.com/comment/skuProductPageComments.action'
		# 解析详情页，获取评论信息
		data = {
		'callback':'fetchJSON_comment98vv229',
		'productId':goodid,
		'score':'0',
		'sortType':'6', #按时间排序
		'page':page,
		'pageSize':'10', # 最多显示十条评论
		'isShadowSku':'0',
		'fold':'1'
		 }
		data = {
			'callback':'fetchJSON_comment98vv762',
			'productId':goodid,
			'score':'0',
			'sortType':'6',
			'page':page,
			'pageSize':'10',
			'isShadowSku':'0',
			'rid':'0',
			'fold':'1'
		 
		 
		 }
		try:
			resp = requests.get(url,params=data,headers=self.headers,proxies=self.proxy)
		except Exception as e:
			print('{}'.format(e))
			logging.error('Fatal error:'+url+'downloaded fail')
			return
		cod = resp.encoding
		result = resp.content.decode(cod)
		reT = r'\w+?\((.*?)\);$'
		res = re.search(reT,result,re.S)
		print(res) # 调试
		if res:
			res = res.group(1)
			res = json.loads(res)
			# print(res)
			try:
				comments = res.get("comments")
			except Exception as e:
				logging.error('comment_detail error:' + e)
				return
			
			if len(comments) == 0:
				self.comment_switch[goodid] = False
				return
		
			myresult = []# 最终要获得的数据 结构
			for i in comments:
				# print(i)
				temp = {}
				temp['crawltime'] = datetime.utcnow().strftime('%Y-%m-%d')
				temp['size'] = i.get('productSize',None)
				temp['comment_time'] = i.get('creationTime',None) # 2015-09-09 11:35:27 
				temp['content'] = i.get('showOrderComment',{}).get("content",i.get('content')) # 这个当然不错的了，我们是用来作图的
				temp['img'] = re.findall(r'http\:\/\/img30\.360buyimg\.com\/shaidan\/jfs\/[\w\/]+?\.jpg',temp.get('content',''))
				if len(temp['img']) == 0:
					temp['img'] = None
				temp['content'] = i.get('content')
				# print(temp['website_url'])
				temp['website'] = 'JD'
				temp['website_url'] = 'http://www.jd.com'
				#http://img30.360buyimg.com/shaidan/jfs/t23899/69/1404782488/83204/3b210e9c/5b5ef8f1N3d24d6b6.jpg
				temp['type'] = self.keyword if keyword is None else keyword
				temp['client'] = self.client if client is None else client
				temp['score'] = i.get('score',None)
				replies = i.get('replies',None)
				temp['replytime'] = None
				if replies is not None:
					try:
						temp['replytime'] = replies[0].get('creationTime',None)
					except IndexError:
						temp['replytime'] = None
				else:
					temp['replytime'] = None # 回复时间
				temp['md5_id'] = self.md5('{}{}'.format(goodid,i.get('id','')))
				temp['goodsname'] = self.goodsname if goodsname is None else goodsname
				norepeat = self.md5('{}{}{}'.format(goodid,i.get('id',''),temp['replytime'] if temp['replytime'] else 'null'))
				if not dbredis.sadd("Reviews_norepeat6",norepeat):
					self.comment_switch[goodid] = False
					#break
				
				myresult.append(temp)
			pipelines = MongodbPipeline()
			try:
				# print(myresult)
				pipelines.insert(myresult)
			except Exception as e:
				logging.error('insert error'+self.keyword+e+'{}'.format(page))
		else:
			self.comment_switch[goodid] = False
		pass
		
	def getfilterid(self,goodid): # 未写完
		pass
		url = 'http://c0.3.cn/stocks'
		data = {
			'callback':'jQuery9573748',
			'type':'getstocks',
			'area':'1_72_2799_0',
			'_':int(time.time()*1000),
			}
			
		resp = requests.get(url,params=data,headers=self.headers,proxies=self.proxy)
		cod = resp.encoding
		cod = 'utf-8' if cod is None else cod
		
		if resp.status_code == 200:
			res = resp.content.decode(cod)
			
			res = re.search(r'\w+?\(.*?\)$',res)
			res = json.loads(res)
			print(res.keys())
			
		
	def run(self):
		if self.lock == False:
			print('{}爬取结束'.format(self.keyword2))
			return
		i = 0
		while self.switch:
			i += 1
			# print(i)
			logging.info(self.goodsname+' '+self.keyword+': '+ 'Page {} start..'.format(i))
			self.__search(page=i,callback = self.parse_comment)
			logging.info(self.goodsname+' '+self.keyword+': '+'Page {} crawled..'.format(i))
			time.sleep(1)
			
			print(self.keyword+'第%s页' %i)
		print('%s 爬取完成' %self.keyword)
		
	def md5(self,rawString):
		if not isinstance(rawString,str):
			return
		s = hashlib.md5(rawString.encode())
		return s.hexdigest()
		
	def Test(self):
		for comment in self.test:
			print(comment)
			return 
			
	def cleanMysql(self):
		if self.lock == False:
			sql = 'delete from {} where type = "{}" and website = "JD"'.format('amazon_Reviews_clean',self.keyword)
			print(sql)
			self.dbmysql.run(sql)
			
	def down(self,callback=None):
		if callback is None:
			callback = self.download_dell
		for i in range(len(goods_list)):
			goodsname = goods_list[i]
			customer = customer_goods.get(goodsname)
			url = url_list[i]
			keywordslist = customer_keyword_list[i]
			callback(url,keywordslist = keywordslist)	
			
	def download_dell(self,url,keywordslist,callback=None):
		if callback is None:
			callback = self.dell_store
		resp = requests.get(url,headers=self.headers,proxies=self.proxy)
		return callback(resp.text,keywordslist = keywordslist)
		
	def dell_store(self,response,keywordslist):
		doc = pq(response)
		result = doc('.j-sku-item a em').items()
		#print(response)
		for res in result:
			goodid = re.findall(r'(\d+)?\.html$',res.parent().attr('href'))
			title = res.text()
			if '差价' in title:
				continue
			if '英寸' not in title:
				continue
			type = None
			for i in keywordslist:
				if i in title:
					type = i
					break
			if type is None:
				continue
			print(type,'type')
			dbredis.sadd('JD_goodid',(goodid[0],type))
		next_page = doc('a.pn-next').attr('href')
		print(next_page)
		if next_page is not None:
			print(next_page)
			return self.download_dell('http://list.jd.com'+next_page,keywordslist)
		else:
			print('导入完成')
			
	def consumer(self):
		#print('消费者')
		#print(dbredis.scard('JD_goodid'))
		while dbredis.scard('JD_goodid') >0:
			print('第{}只爬虫正在运行'.format(self.tag))
			record = json.loads(dbredis.spop('JD_goodid').decode().replace("'",'"').replace('(','[').replace(')',']'))
			if record is None:
				continue
			goodid = record[0]
			keyword = record[1]
			#print(keyword)
			goodsname = keywords_type.get(keyword)
			#print(goodsname)
			keyword = goodsname + ' ' + keyword
			print(keyword,goodid)
			self.parse_comment(goodid = goodid,keyword=keyword,goodsname=goodsname)
		pass
if __name__ == "__main__":
	test = reviews(debug=False)
	url = 'http://list.jd.com/list.html?cat=670,677,688&ev=exbrand_5821&page=1&sort=sort_commentcount_desc&trans=1&JL=6_0_0#J_main'
	test.down() #下载店铺信息
	#test.consumer()
	#result = test.comment_detail(goodid = '4702732',page=0,callback=None,meta=None,keyword='Dell P2418HT',goodsname=None,client='Dell')
	# test.run()
    
	pass