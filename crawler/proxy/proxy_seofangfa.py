# coding=utf-8
from proxy import Proxy
from lxml import etree
import socket

socket.setdefaulttimeout(20)

class proxy_seofangfa(Proxy):
    def __init__(self):
        super().__init__()
        
    def get_url(self,page):
        return 'http://ip.seofangfa.com/proxy/{}.html'.format(page)
            
    def parse(self,result):
        html = etree.HTML(result)
        records = html.xpath('//tbody/tr')
        for record in records:
            host =self.clean(record.xpath(r'./td[1]/text()'))
            port = self.clean(record.xpath(r'./td[2]/text()'))
            self.queue.put((self.clean(host),self.clean(port)))
            print((self.clean(host),self.clean(port)))
        self.page += 1
        return len(records) #返回解析出来的数据个数
        
if __name__ == '__main__':
    test = proxy_seofangfa()
    test.run()
    