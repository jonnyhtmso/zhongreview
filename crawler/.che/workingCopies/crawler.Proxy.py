import random

proxy_list = []
with open('proxy/proxy.txt','r') as f:
    proxy_list = f.readlines()
raw_proxy_list = set()
max_timeout = 10
for proxy in proxy_list:
    proxy = proxy.strip()
    if not proxy:
        continue
    proxy_temp = proxy.split(' ')
    proxy_time = float(proxy_temp[1].strip())
    if proxy_time <= max_timeout:
        raw_proxy_list.add(proxy_temp[0].strip())
        
raw_proxy_list = list(raw_proxy_list)
    
def get_one_proxy():
    if raw_proxy_list:
        return random.choice(raw_proxy_list)
    
def get_many_proxy(num= None):

    if num is None:
        num = len(raw_proxy_list)
    if num > len(raw_proxy_list):
        num = len(raw_proxy_list)
    return random.sample(raw_proxy_list, num)


if __name__ == '__main__':

    proxy = get_many_proxy()
    print(proxy)