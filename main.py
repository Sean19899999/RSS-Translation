# coding:utf-8 
import configparser
from pygtrans import Translate
from bs4 import BeautifulSoup
import sys
import os
from urllib import request
import urllib
# pip install pygtrans -i https://pypi.org/simple
# ref:https://zhuanlan.zhihu.com/p/390801784
# ref:https://beautifulsoup.readthedocs.io/zh_CN/latest/
# ref:https://pygtrans.readthedocs.io/zh_CN/latest/langs.html
import hashlib

def get_md5_value(src):
    _m = hashlib.md5()
    _m.update(src.encode('utf-8'))
    return _m.hexdigest()
    
config = configparser.ConfigParser()
config.read('test.ini',encoding='utf-8')
secs=config.sections()

def get_cfg(sec,name):
    return config.get(sec,name).strip('"')

def set_cfg(sec,name,value):
    config[sec][name]='"%s"'%value

def get_cfg_tra(sec):
    cc=config.get(sec,"action").strip('"')
    target=""
    source=""
    if cc == "auto":
        source  = 'auto'
        target  = 'zh-CN'
    else:
        source  = cc.split('->')[0]
        target  = cc.split('->')[1]
    return source,target

BASE=get_cfg("cfg",'base')
try:
    os.makedirs(BASE)
except:
    pass
links=[]

def tran(sec):
    out_dir= BASE + get_cfg(sec,'name')
    url=get_cfg(sec,'url')
    max_item=int(get_cfg(sec,'max'))
    old_md5=get_cfg(sec,'md5')
    source,target=get_cfg_tra(sec)
    global links

    links+=[" - %s [%s](%s) -> [%s](%s)\n"%(sec,url,url,get_cfg(sec,'name'),out_dir)]

    GT = Translate()
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'
        }
    req = urllib.request.Request(url, headers=headers)

    rss_doc=request.urlopen(req).read().decode('utf8')
    new_md5= get_md5_value(rss_doc)

    if old_md5 == new_md5:
        return
    else:
        set_cfg(sec,'md5',new_md5)

    soup = BeautifulSoup(rss_doc, 'xml')
    items = soup.find_all('item')
    for idx, e in enumerate(items):
        if idx > max_item:
            e.decompose()

    for idx, item in enumerate(soup.find_all('item')):
        title = item.find('title').text
        description = item.find('description').text

        translated_title = GT.translate(title, target=target, source=source).translatedText
        translated_description = GT.translate(description, target=target, source=source).translatedText

        item.find('title').string = translated_title
        item.find('description').string = translated_description

    content= str(soup)

    with open(out_dir,'w',encoding='utf-8') as f:
        f.write(content)
    print("GT: "+ url +" > "+ out_dir)

for x in secs[1:]:
    tran(x)
    print(config.items(x))

with open('test.ini','w') as configfile:
    config.write(configfile)

YML="README.md"

f = open(YML, "r+", encoding="UTF-8")
list1 = f.readlines()
f.seek(0)
f.truncate()
list1[2:2] = links
list1 = "".join(list1)
f.write(list1)
f.close()
print('Updated %s'%YML)
