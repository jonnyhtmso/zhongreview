# coding=utf8
import requests
from lxml import etree
from multiprocessing.pool import ThreadPool
import multiprocessing
import os
import time
import socket

socket.setdefaulttimeout(20)

'''
数据存储格式 proxy timeout 地理位置
'''

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
# 快代理
class Proxy(object):
    def __init__(self):
        self.test_url = 'https://www.taobao.com'
        mgr = multiprocessing.Manager()
        self.queue = mgr.Queue()
        self.queue2 = mgr.Queue()
        self.page = 1
        self.max_page = 100 #最大爬取页面(获取代理的时候使用)
        self.test_count = 3 #最多测试三次
        self.num_thread = 50
        self.count = [0]*self.num_thread #线程相关
        self.se = set() #去重
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        self.timeout = 20 #超时时间5秒
    def get_headers(self):
    
        return {'getproxy':self.headers,'test':self.headers}
    def get_url(self,page):
       return 'https://www.kuaidaili.com/free/inha/{}/'.format(page)
    def clean(self,s):
        if isinstance(s,(list,tuple)):
            s = s[0] if s else None
        if isinstance(s,str):
            s = s.strip()
        return s
        
    def parse(self,result):
        html = etree.HTML(result)
        records = html.xpath('//tbody/tr')
        for record in records:
            self.queue.put((self.clean(record.xpath('./td[1]/text()')),self.clean(record.xpath('./td[2]/text()'))))
            print((self.clean(record.xpath('./td[1]/text()')),self.clean(record.xpath('./td[2]/text()'))))
        self.page += 1
        return len(records) #返回解析出来的数据个数
        
    def getproxy(self):
        self.page = 1
        while self.page <self.max_page: #只取最近一百页
            time.sleep(1)
            print('正在获取第{}页数据'.format(self.page))
            url = self.get_url(self.page)
            if url is None:
                return
            headers = self.get_headers().get('getproxy',self.headers)
            resp = requests.get(url,headers=headers)
            result = resp.text
            #print(result)
            temp = self.parse(result) #返回的是解析数据的个数
            if temp ==0:
                break

    def test(self,i):
        while self.count[i] < 5:
            if self.queue.empty():
                time.sleep(60)
                self.count[i] += 1
                continue
            record = self.queue.get()
            print('正在测试{}...'.format(record[0]))
            temp_proxies = '{}:{}'.format(*record)
            proxies = {'http':temp_proxies,'https':temp_proxies}
            url = 'https://www.taobao.com'
            if temp_proxies.strip() in self.se:
                continue
            for i in range(self.test_count):
                start_time = time.time()
                headers = self.get_headers().get('test',self.headers)
                resp = requests.get(url,headers=headers,proxies=proxies,timeout = self.timeout)
                end_time = time.time()
                print(resp.status_code)
                if resp and resp.status_code == 200:
                    self.queue2.put((temp_proxies.strip(),'%0.2f' %(end_time - start_time)))
                    self.se.add(temp_proxies.strip())
                    print(temp_proxies+' √')
                    break
                
    def saveToFile(self):
        templist = []
        while not self.queue2.empty():
            record = self.queue2.get()
            templist.append('{} {}'.format(*record))
        templist = map(lambda x:x.strip(),templist)
        with open('proxy.txt','w') as f:
            for temp in templist:
                f.write(temp+'\n')
                
    
    def run(self):
        print('读取原始数据...')
        templist = []
        if os.path.exists('proxy.txt') and os.path.isfile('proxy.txt'):
            with open('proxy.txt','r') as f:
                templist = f.readlines()
            for temp in templist:
                temp = temp.strip().split(' ')
                if temp:
                    temp = temp[0]
                    temp = temp.split(':')
                    self.queue.put(temp)
                else:
                    continue
        if os.path.exists('raw_proxy.txt') and os.path.isfile('raw_proxy.txt'):
            with open('raw_proxy.txt','r') as f:
                templist = f.readlines()
            for temp in templist:
                temp = temp.strip()
                if temp:
                    temp = temp.split(':')
                    if len(temp) !=2:
                        continue
                    self.queue.put(temp)
                else:
                    continue
        
        print('读取原始数据完成')
        print('正在获取proxy...')
        self.getproxy()
        print('数据获取完成...')
        print('数据清洗中')
        pool = ThreadPool(self.num_thread)
        for i in range(self.num_thread):
            pool.apply_async(func=self.test,args = (i,))
        pool.close()
        pool.join()
        print('数据清洗完成')
        print('正在保存数据')
        self.saveToFile()
        print('数据保存完成,共取得{}条数据'.format(len(self.se)))
        
    def testclass(self):
        print('正在获取proxy...')
        self.getproxy()
        print('数据获取完成...')
        print('数据清洗中')
        pool = ThreadPool(self.num_thread)
        for i in range(self.num_thread):
            pool.apply_async(func=self.test,args = (i,))
        pool.close()
        pool.join()
        print('数据清洗完成')
        print('正在保存数据')
        #self.saveToFile()
        print('数据保存完成,共取得{}条数据'.format(len(self.se)))
    
    
if __name__ == '__main__':
    test = Proxy()
    test.run()
    