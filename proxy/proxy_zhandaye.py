from proxy import Proxy
from lxml import etree
import socket
from datetime import date
import requests

socket.setdefaulttimeout(20)

class zhandaye(Proxy):
    def __init__(self):
        super().__init__()
        self.urllist = []
    
    def get_headers(self):
        result = super().get_headers()
        result = result.get('getproxy',{})
        result['Referer'] = 'http://ip.zdaye.com/dayProxy/2019/1/1.html'
        return {'getproxy':result,'test':self.headers}
        
    def get_url(self,page):
        if page == 1:
            headers = self.get_headers().get('getproxy',self.headers)
            url = 'http://ip.zdaye.com/dayProxy/2019/1/1.html' #只获取第一页信息,这个url以后修改
            resp = requests.get(url,headers=headers)
            result = resp.content
            html = etree.HTML(result)
            self.urllist.extend(html.xpath(r'//div[@class="title"]/a/@href'))
            
        if self.urllist:
            return 'http://ip.zdaye.com' + self.urllist.pop()
        else:
            return
            
            
    def parse(self,result):
        #print(result[5000:])
        print(result)
        html = etree.HTML(result)
        records = html.xpath('//div[@class="cont"]//text()')
        for record in records:
            record = record.strip()
            if not record:
                continue
            record = record.split('@')[0]
            record = record.split(':')
            host , port = record
            print(host,port)
            self.queue.put((self.clean(host),self.clean(port)))
            #print((self.clean(host),self.clean(port)))
        self.page += 1
        return len(records) #返回解析出来的数据个数
        
if __name__ == '__main__':
    test = zhandaye()
    test.testclass()
