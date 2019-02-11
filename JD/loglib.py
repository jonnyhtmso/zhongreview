import logging
import configparser

# 获取config
config = configparser.RawConfigParser()
config.read('config.txt',encoding="utf-8")

logpath = config.get('LOG','path')
logging.basicConfig(filename=logpath
					,filemode='a'
					, level=logging.INFO
					, format='%(asctime)s %(message)s'
					, datefmt='%Y/%m/%d %I:%M:%S %p'
					
					)