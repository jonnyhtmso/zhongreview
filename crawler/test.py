# -*- coding:utf-8 -*-

import requests

url = 'https://www.xicidaili.com'
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
headers['Referer'] = 'https://www.xicidaili.com/'
headers['Connection'] = 'keep-alive'
headers['Cache-Control'] = 'max-age=0'
headers['Upgrade-Insecure-Requests'] = '1'
headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
headers['Accept-Encoding'] = 'gzip, deflate, br'  
headers['zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'] = 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
headers['Cookie'] = '_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTY4M2FmNWE5OTkzZWQyZGI4ZDg1ZTg5NDM5ZmY3MWZkBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMWdzUG5lN0lzaW5EWklzaGRLbVVIcGhoT1A1ckFBaEZTelV1V21TczFZbU09BjsARg%3D%3D--6eac5be4d7548b4c42b4659c78e25b8a03df2e4a; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1545620129,1545703637; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1545703642'

resp = requests.get(url, headers =headers)
print(resp.status_code)