import requests
from lxml import etree
import re


def checkLogin(func):
    def temp(self, *args, **kwargs):
        if self.login_switch:
            return func(self, *args, **kwargs)
        else:
            print('请登陆之后再使用')
    return temp

class DotTk(object):
    def __init__(self):
        self.session = requests.session()
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
        self.login_switch = False
        self.dns_list = ['athena.ns.cloudflare.com','thomas.ns.cloudflare.com']
        self.suffix = ['tk','ml','ga','cf','gq']
        pass


    def clean(self,s):
        if isinstance(s,(list,tuple)):
            s = s[0].strip() if s else ''
        else:
            s = ''
        return s

    def login(self,user,passwd):
        url2 = 'https://my.freenom.com/clientarea.php?language=english'
        resp2 = self.session.get(url2,headers = self.headers)
        html = etree.HTML(resp2.text)
        Token = html.xpath(r'//input[@name="token"]/@value')
        Token = Token[0] if Token else ''
        url3 = 'https://my.freenom.com/dologin.php'
        data3 = {
            'token': Token,
            'username': user,
            'password': passwd
        }
        headers3 = {'Referer':'https://my.freenom.com/clientarea.php?language=english'}
        headers3.update(self.headers)
        resp3 = self.session.post(url3,data=data3,headers=headers3)
        if 'View cart'in resp3.text:
            print('登陆成功！！')
            self.login_switch = True

    def search(self,domain):
        if not re.search(r'^[a-z0-9]+?$',domain):
            print('请输入一个正确的值')
            return
        result= {'status':0,'description':'您提交的域名已经存在，请您重试。','data':[]}
        url = 'https://my.freenom.com/includes/domains/fn-available.php'
        data = {
            'domain':domain,
            'tld':''
        }
        resp = requests.post(url,data=data,headers=self.headers)
        try:
            temp = resp.json()
        except:
            return
        temp = temp.get('free_domains')
        temp = filter(lambda x:x.get('type','')=='FREE' and x.get('status','')== 'AVAILABLE' and x.get('price_int','')=='0'and x.get('price_cent','')=='00',temp)
        domainlist = list(map(lambda x:x.get('domain','xxx')+x.get('tld','xxx'),temp))
        length = len(domainlist)
        if length:
            result['status'] = 1
            result['description'] = '共找到域名{}个,希望能满足您的需求'.format(length)
            result['data'] = domainlist

        return result

    @checkLogin
    def buyadomain(self,domainlist):
        if not isinstance(domainlist,(list,tuple)):
            return


    def addalldomain(self,domain):
        result = self.search(domain)
        if result is None:
            print('系统发生错误，请与管理员联系.')
            return
        if result.get('status',0) == 0:
            print('没有找到您需要的域名')
            return
        count = 0
        for tempdoamin in result.get('data',[]):
            result = self.adddomain(*tempdoamin.split('.'))
            if result:
                count += 1
        return {'count':count,'description':'共成功添加了{}个域名'.format(count)}

    @checkLogin
    def adddomain(self,domain,tld):
        url = 'https://my.freenom.com/includes/domains/fn-additional.php'
        headers = {'Referer':'https://my.freenom.com/domains.php'}
        headers.update(self.headers)
        data = {
            'domain':domain,
            'tld':tld
        }
        resp = self.session.post(url,data=data,headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            print(result)
            if result.get("available",0) == 1:
                return True

    def update(self,domain):
        pass

    @checkLogin
    def list_all_domain(self):
        url4 = 'https://my.freenom.com/clientarea.php?action=domains'
        headers4 = {'Referer':'https://my.freenom.com/clientarea.php?language=english'}
        headers4.update(self.headers)
        resp4 = self.session.get(url4,headers=headers4)
        result = resp4.text
        html = etree.HTML(result)
        record_list = html.xpath(r'//tbody/tr')
        result = []
        for record in record_list:
            name = self.clean(record.xpath(r'./td[1]//text()'))
            Registration_Date = self.clean(record.xpath(r'./td[2]/text()'))
            Expiry_date = self.clean(record.xpath(r'./td[3]/text()'))
            status = self.clean(record.xpath(r'./td[4]//text()'))
            type = self.clean(record.xpath(r'./td[5]//text()'))
            domain_id = self.clean(re.findall(r'id=(\d+?)$',self.clean(record.xpath(r'./td[6]//a/@href'))))

            result.append({'name':name,'Registration_Date':Registration_Date,'Expiry_date':Expiry_date,'status':status,'type':type,'domain_id':domain_id})
        return result

    @checkLogin
    def set_dns(self,domain_id,dns_list = None):
        if dns_list is None:
            dns_list = self.dns_list
        url1 = 'https://my.freenom.com/clientarea.php?action=domaindetails&id={}'.format(domain_id)
        headers1 = {'Referer':'https://my.freenom.com/clientarea.php?action=domains'}
        headers1.update(self.headers)
        resp1 = self.session.get(url1,headers=headers1)
        html = etree.HTML(resp1.text)
        Token = html.xpath(r'//input[@name="token"]/@value')
        Token = Token[0] if Token else ''

        url2 = 'https://my.freenom.com/clientarea.php?action=domaindetails'
        data2 = {
            'sub':'savens',
            'nschoice':'custom'
        }
        data2['token'] = Token
        data2['id'] = domain_id
        for i in range(1,6):
            if i >len(dns_list):
                data2['ns{}'.format(i)]=''
            else:
                data2['ns{}'.format(i)] = dns_list[i-1]
        headers2 = {'Referer': url1}
        headers2.update(self.headers)
        resp2 = self.session.post(url2,data=data2,headers=headers2)
        if 'Changes Saved Successfully!' in resp2.text:
            print('dns更新成功！')
        return {'status':1,'description':'DNS更新成功！'}

        pass

    def vistallweb(self):
        pass

if __name__ == '__main__':
    test = DotTk()

    test.login('860003213@qq.com','04120412')
    #result = test.list_all_domain()

    #result = test.set_dns('1040640524')
    result = test.addalldomain('zhongshan')
    print(result)