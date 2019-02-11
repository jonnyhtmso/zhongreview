import requests

headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

headers['Referer'] = 'http://www.xicidaili.com'
url ='http://www.xicidaili.com/nn/'
resp = requests.get(url,headers=headers)
print(resp.status_code)
print(resp.text)
