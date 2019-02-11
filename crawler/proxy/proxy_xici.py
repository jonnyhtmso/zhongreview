from proxy import Proxy
from lxml import etree

# 西刺代理
class xici(Proxy):
    def __init__(self):
        super().__init__()
    def get_url(self,page):
        return 'http://www.xicidaili.com/nn/{}'.format(page)
    def parse(self,result):
        html = etree.HTML(result)
        result_list = html.xpath('//tbody/tr')
        for res in result_list:
            host = res.xpath(r'./td[2]/text()')
            port = res.xpath(r'./td[3]/text()')
            print(host,port)
        return len(result_list)

if __name__ == '__main__':
    test = xici()
    test.run()