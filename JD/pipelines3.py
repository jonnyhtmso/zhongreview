# 数据管道文件
import pymysql
import pymongo
import configparser
from loglib import logging
import re
import time
import json

# 获取config
config = configparser.RawConfigParser()
config.read('config.txt',encoding="utf-8")

mongohost = config.get('MONGODB','host')
mongoport = config.get('MONGODB','port')

#mongodb
class MongodbPipeline(object):
	def __init__(self):
		try:
			self.mconn = pymongo.MongoClient(mongohost,int(mongoport))
			self.db = self.mconn['eshop']
			self.collection = self.db['reviews_JD6']
		except Exception as e :
			logging.error('Fatal Error :Mongodb connect get an Fatal Error : %s'  %e)
		else:
			logging.info('Mongodb connect success!')
		
	def insert(self,doc):
		if isinstance(doc,(list,set,tuple)):
			try:
				self.collection.insert_many(doc) # 插入多个
			except Exception as e:
				logging.info('insert Failed,{}'.format(e))
		elif isinstance(doc,dict):
			try:
				self.collection.insert_one(doc) #测试时候使用
			except Exception as e:
				logging.info('insert Failed,{}'.format(e))
			
	def find(self,condition = None):
		if condition is None :
			try:
				result = self.collection.find()
			except Exception as e:
				logging.error('something wrong with geting a record')
				return 
		else:
			try:
				result = self.collection.find(condition)
			except Exception as e:
				logging.error('something wrong with geting a record')
				return 
		return list(result) if result else []
		
	def delete(self,condition = None):
		'''当没有输入条件的时候,会删除所有的结果'''
		condition = {} if condition is None and condition is dict  else condition
		try:
			num = self.collection.remove({})
		except Exception as e:
			logging.error('"delete" get an Fatal Error {}'.format(e))
		return num if num else 0
		pass
	
	def count(self,condition = None):
		if condition is None:
			return self.collection.count()
		elif isinstance(condition,(dict,)):
			print(condition)
			return self.collection.count(condition)
		
	def __del__(self):
		try:
			self.mconn.close()
		except Exception as e:
			pass

# mysql			
mysqlconfig = {}
mysqlconfig['host'] = config.get('MySQL','mysqlserver')
mysqlconfig['port'] = int(config.get('MySQL','mysqlport'))
mysqlconfig['user'] = config.get('MySQL','mysqluser')
mysqlconfig['password'] = config.get('MySQL','mysqlpassword')
mysqlconfig['db'] = config.get('MySQL','database')
mysqlconfig['charset'] = config.get('MySQL','charset')

	
class MysqlPipeline(object):
	def __init__(self):
		try:
			# print(mysqlconfig)
			self.conn = pymysql.connect(**mysqlconfig)
		except Exception as e:
			logging.error('Fatal Error :Mysql connect get an Fatal Error : %s'  %e)
		else:
			logging.info('Mysql connect success')
	def __sql(self,pattern):
		"""
		处理sql语句
		"""
		if pattern is None:
			print("error ,got a wrong sql")
			return
		cur = self.conn.cursor()
		pattern = pattern.strip()

		result = {"status":0,"type":'',"error":'',"value":''}
		firstword = pattern.split(' ')
		firstword= firstword[0].upper()
		if firstword  in  ["SELECT",'SHOW']: #查找
			try:
				cur.execute(pattern)
				# result['value'] = cur.fetchall()
				result['status'] = 1
				result['type'] = "insert"
			except Exception as e:
				print(e)
				result['value'] = ''
				result['status'] = 0
				result['type'] = ""
				result['error'] = "系统在执行查询操作的时候发生错误" + '' + 'e'
			else:
				li = []
				for i in  cur.fetchall():
					li.append(i)
				result['value'] = li

			pass
		if firstword == "INSERT" or firstword == "REPLACE":# 插入
			try:
				cur.execute(pattern)
				pass
			except Exception as e :
				self.conn.rollback()
				print(e)
				result['value'] = ''
				result['status'] = 0
				result['type'] = ""
				result['error'] = "系统在执行插入操作的时候发生错误" + '' + 'e'
			else:
				self.conn.commit()
				result['value'] = '[]'
				result['status'] = 1
				result['type'] = "INSERT"
				result['error'] = ''
		if firstword == "DELETE":# 删除
			try:
				cur.execute(pattern)
				pass
			except Exception as e:
				self.conn.rollback()
				print(e)
				result['value'] = ''
				result['status'] = 0
				result['type'] = ""
				result['error'] = "系统在执行删除操作的时候发生错误" + '' + 'e'
			else:
				self.conn.commit()
				result['value'] = '[]'
				result['status'] = 1
				result['type'] = "DELETE"
				result['error'] = ''
		if firstword == "UPDATE": # 更新
			try:
				cur.execute(pattern)
				self.conn.commit()
				pass
			except Exception as e:
				self.conn.rollback()
				print(e)
				result['value'] = ''
				result['status'] = 0
				result['type'] = ""
				result['error'] = "系统在执行更新操作的时候发生错误" + '' + 'e'
			else:
				self.conn.commit()
				result['value'] = '[]'
				result['status'] = 1
				result['type'] = "UPDATE"
				result['error'] = ''
				
		cur.close()
		return result
		
	def run(self,pattern):
		return self.__sql(pattern)
			
	def __del__(self):
		try:
			self.conn.close()
		except Exception as e:
			pass
		 

	
	
	#将mongodb数据导入mysql	
def jd():
	sqllist = []
	sql0 = 'replace into eshop (MD5_id,content,creationTime,score,referenceName,referenceTime,source) VALUES '
	for i in range(len(temp)):
		_ = {}
		_["MD5_id"] = temp[i].get("md5_id",None)
		_["content"] = temp[i].get("content",None)
		_["creationTime"] = temp[i].get("creationTime",None)
		_["score"] = temp[i].get("score",None)
		_["referenceName"] = temp[i].get("referenceName",None)
		_["referenceTime"] = temp[i].get("referenceTime",None)
		_["source"] = temp[i].get("source",None)
		_["content"] = re.sub(r"\'","\\\'",_["content"])
		_["content"] = re.sub(r'\"','\\\"',_["content"])
		# _["content"] = re.sub(r"\'","\\\'",_["content"])
		# print(_)
		if _["MD5_id"] is None:
			logging.info("MD5_id is none:")
			continue
		else:
			sqltemp = "({},{},{},{},{},{},{})".format(
												"'{}' ".format(_["MD5_id"])
												,"'{}' ".format(_["content"])
												,"'{}' ".format(_["creationTime"])
												,"{}".format(_["score"])
												,"'{}' ".format(_["referenceName"])
												,"'{}' ".format(_["referenceTime"])
												,"'{}' ".format(_['source'])
			)
			sqllist.append(sqltemp)
		if i%10000 == 0:
			print('#')
			time.sleep(1)
			
	# 处理插入数量过大问题
	length = len(sqllist)
	first = 0
	last = 0
	
	while first < length:
		last = first + 20000
		if last >length:
			last = -1
			sqllisttemp = sqllist[first:]
			sql = sql0 + '\n,'.join(sqllisttemp)
			
			mysqlconn = MysqlPipeline()
			try:
				s = mysqlconn.run(sql)
				print(s)
				print('结束')
			except Exception as e:
				print(e)
			break
		else:
			sqllisttemp = sqllist[first:last]
			sql = sql0 + '\n,'.join(sqllisttemp)
			
			mysqlconn = MysqlPipeline()
			try:
				s = mysqlconn.run(sql)
				print(s)
			except Exception as e:
				print(e) 
			print(first,'~',last)
			first = last
			
def amazon(raw_data):
	temp = raw_data
	sqllist = []
	sql0 = 'replace into JD_Reviews5 (md5_id,website,website_url,goodsname,client,type,size,comment_time,content,crawltime,replytime,img,score) VALUES '
	for i in range(len(temp)):
		_ = {}
		_['md5_id'] = temp[i].get('md5_id',None)
		if _['md5_id'] is None:
			continue
		_["website"] = temp[i].get("website",None)
		_["website_url"] = temp[i].get("website_url",None)
		_["goodsname"] = temp[i].get("goodsname",None)
		_["client"] = temp[i].get("client",None)
		_["type"] = temp[i].get("type",None)
		_["size"] = temp[i].get("size",None)
		_["comment_time"] = temp[i].get("comment_time",None)
		_["content"] = temp[i].get("content",None)
		_["crawltime"] = temp[i].get("crawltime",None)
		_["replytime"] = temp[i].get("replytime",None)
		_["img"] = temp[i].get("img",None)
		if isinstance(_['img'],(list)):
			_['img'] = json.dumps(_['img']).replace("\'","\\\'")
		_["score"] = temp[i].get("score",None)
		
		_["content"] = re.sub(r"\\",r"\\"+r"\\", _["content"])
		_["content"] = re.sub(r"'",r"\'",_["content"])
		_["content"] = re.sub(r'"',r'\"',_["content"])
		
		# if _["content"].find('\\') >= 0 :
			# _["content"] = _["content"].replace('\\',"\\\\")
		# elif _["content"].find('\"') >= 0 :
			# _["content"] = _["content"].replace('\"','\\\"')
		# elif _["content"].find('\'') >= 0 :
			# _["content"] = _["content"].replace('\'',"\\\'")
		# _["content"] = re.sub(r"\'","\\\'",_["content"])
		# print(_)
		# if _["MD5_id"] is None:
			# logging.info("MD5_id is none:")
			# continue
		# else:
		# print(_["size"],'size',temp[i].get('size'))
		sqltemp = "({},{},{},{},{},{},{},{},{},{},{},{},{})".format(
												"'{}' ".format(_["md5_id"]) if _["md5_id"] is not None else 'NULL'
												,"'{}' ".format(_["website"]) if _["website"] is not None else 'NULL'
												,"'{}' ".format(_["website_url"]) if  _["website_url"] is not None else 'NULL'
												,"'{}' ".format(_["goodsname"]) if _["goodsname"] is not None else 'NULL'
												,"'{}' ".format(_["client"]) if _["client"] is not None else 'NULL'
												,"'{}' ".format(_["type"]) if _["type"] is not None else 'NULL'
												,"'{}' ".format(_["size"]) if _["size"] is not None else 'NULL'
												,"'{}' ".format(_["comment_time"]) if _["comment_time"] is not None else 'NULL'
												,"'{}' ".format(_["content"]) if _["content"] is not None else 'NULL'
												,"'{}' ".format(_["crawltime"]) if _["crawltime"] is not None else 'NULL'
												,"'{}' ".format(_["replytime"]) if _["replytime"] is not None else 'NULL'
												,"'{}' ".format(_["img"]) if _["img"] is not None else 'NULL'
												,"{}".format(_["score"]) if _["score"] is not None else 'NULL'
			)
		# print(sqltemp)
		sqllist.append(sqltemp)
		if i%10000 == 0:
			print('#')
			time.sleep(1)
			
	# 处理插入数量过大问题
	# sqllist = sqllist[487632:487635]
	length = len(sqllist)
	first = 0
	last = 0
	
	while first < length:
		last = first + 20000
		if last >length:
			last = -1
			sqllisttemp = sqllist[first:]
			sql = sql0 + '\n,'.join(sqllisttemp)
			
			mysqlconn = MysqlPipeline()
			try:
				# print(sql)
				s = mysqlconn.run(sql)
				print(s)
				print('结束')
			except Exception as e:
				print(e)
			break
		else:
			sqllisttemp = sqllist[first:last]
			sql = sql0 + '\n,'.join(sqllisttemp)
			
			mysqlconn = MysqlPipeline()
			try:
				s = mysqlconn.run(sql)
				print(s)
			except Exception as e:
				print(e) 
			print(first,'~',last)
			first = last
			
if __name__ == "__main__":
	test = MongodbPipeline()
	temp = test.find()
	# print(temp[-13])
	# print(test.count({'website':'JD'}))
	#amazon(temp)
	print(len(temp))


