#!/bin/sh
echo "start update!" >> proxy.log
date >> proxy.log
bash /etc/profile
bash /home/user/.profile
/usr/local/bin/python /projects/crawler/proxy/proxy_89.py >> proxy.log
/usr/local/bin/python /projects/crawler/proxy/proxy_kuaidaili.py >> proxy.log
date >> proxy.log
echo "Update Success!" >> proxy.log