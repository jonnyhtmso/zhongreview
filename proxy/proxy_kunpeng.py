from proxy import Proxy
from lxml import etree
import socket

socket.setdefaulttimeout(20)

class kunpeng(Proxy):
    def __init__(self):
        super().__init__()
    def get_url(self,page):
        if page == 1:
            return 'http://www.site-digger.com/html/articles/20110516/proxieslist.html'
            
    def parse(self,result):
        print(result[5000:])
        html = etree.HTML(result)
        records = html.xpath('//tbody/tr')
        for record in records:
            temp =self.clean(record.xpath(r'./td[1]/text()'))
            #print(temp)
            if not temp:
                continue
            temp = temp.split(':')
            if len(temp) <2:
                continue
            host = temp[0]
            port = temp[1]
            self.queue.put((self.clean(host),self.clean(port)))
            #print((self.clean(host),self.clean(port)))
        self.page += 1
        return len(records) #返回解析出来的数据个数
        
if __name__ == '__main__':
    test = kunpeng()
    test.run()
    