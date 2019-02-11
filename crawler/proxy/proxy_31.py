from proxy import Proxy
from lxml import etree
import socket
from datetime import date
import requests
import re

socket.setdefaulttimeout(20)

class proxy_31(Proxy):
    def __init__(self):
        super().__init__()
        self.urllist = []
    
    def get_headers(self):
        result = super().get_headers()
        result = result.get('getproxy',{})
        result['Cookie'] = 'Hm_lvt_c04918a39ff11e02096f3cd664c5ada6=1547693618; _xsrf=2|a8ef327a|d9f371d5e0ec1494fea337c46b05aa38|1547693634; user="2|1:0|10:1547693665|4:user|12:aG56aG9uZw==|435066fa30123c0ba87c99dfb55594db023c275e1ec4255ce1b4aa0af0db96af"; Hm_lpvt_c04918a39ff11e02096f3cd664c5ada6=1547693707'
        return {'getproxy':result,'test':self.headers}
        
    def get_url(self,page):
        if page == 1:
            return 'https://31f.cn/search/?port=&area=&proto=anonymous&export=txt'
            
            
    def parse(self,result):
        result = re.split(r'\s',result.strip())
        result = list(filter(lambda x:x.strip(),map(lambda x:x.strip(),result)))
        for record in result:
            record = record.split(':')
            #print(record)
            host , port = record
            print(host,port)
            
            self.queue.put((self.clean(host),self.clean(port)))
            #print((self.clean(host),self.clean(port)))
        self.page += 1
        return len(result) #返回解析出来的数据个数
        
if __name__ == '__main__':
    test = proxy_31()
    test.testclass()
