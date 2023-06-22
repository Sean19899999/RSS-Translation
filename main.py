# coding:utf-8 
import configparser
from pygtrans import Translate
from bs4 import BeautifulSoup
import sys
import os
from urllib import request
import urllib
import hashlib
import datetime
import time
from rfeed import *
import feedparser

# Function to get MD5 value
def get_md5_value(src):
    _m = hashlib.md5()
    _m.update(src.encode('utf-8'))
    return _m.hexdigest()

# Functions to get current time and subtitle of a feed item
def getTime(e):
    try:
        struct_time = e.published_parsed
    except:
        struct_time = time.localtime()
    return datetime.datetime(*struct_time[:6])

def getSubtitle(e):
    try:
        sub = e.subtitle
    except:
        sub = ""
    return sub

# Class to translate feed items' title and summary
class GoogleTran:
    def __init__(self, url, source='auto', target='zh-CN'):
        self.url = url
        self.source = source
        self.target = target

        self.d = feedparser.parse(self.url)
        self.GT = Translate()

    def tr(self, content):
        tt = self.GT.translate(content, target=self.target, source=self.source)
        try:
            return tt.translatedText
        except:
            return ""

    def get_newcontent(self, max=2):
        item_list = []
        if len(self.d.entries) < max:
            max = len(self.d.entries)
        for entry in self.d.entries[:max]:
            one = Item(
                title=self.tr(entry.title),
                link=entry.link,
                description=self.tr(entry.summary),
                guid=Guid(entry.link),
                pubDate=getTime(entry))
            item_list.append(one)
        feed = self.d.feed
        newfeed = Feed(
            title=self.tr(feed.title),
            link=feed.link,
            description=self.tr(getSubtitle(feed)),
            lastBuildDate=getTime(feed),
            items=item_list)
        return newfeed.rss()

# Reading configuration
config = configparser.ConfigParser()
config.read('test.ini', encoding='utf-8')
secs = config.sections()

# Functions to get and set config
def get_cfg(sec, name):
    return config.get(sec, name).strip('"')

def set_cfg(sec, name, value):
    config[sec][name] = '"%s"' % value

# Function to get source and target languages
def get_cfg_tra(sec):
    cc = config.get(sec, "action").strip('"')
    if cc == "auto":
        source  = 'auto'
        target  = 'zh-CN'
    else:
        source  = cc.split('->')[0]
        target  = cc.split('->')[1]
    return source, target

# Directory for output
BASE = get_cfg("cfg", 'base')
try:
    os.makedirs(BASE)
except:
    pass

links = []
def tran(sec):
    out_dir = BASE + get_cfg(sec, 'name')
    url = get_cfg(sec, 'url')
    max_item = int(get_cfg(sec, 'max'))
    old_md5 = get_cfg(sec, 'md5')
    source, target = get_cfg_tra(sec)
    global links

    links += [" - %s [%s](%s) -> [%s](%s)\n" % (sec, url, url, get_cfg(sec, 'name'), out_dir)]

    new_md5 = get_md5_value(url) # new md5 value based on url

    if old_md5 == new_md5:
        return
    else:
        set_cfg(sec, 'md5', new_md5)

    c = GoogleTran(url, target=target, source=source).get_newcontent(max=max_item)

    with open(out_dir, 'w', encoding='utf-8') as f:
        f.write(c)
        print("GT: "+ url +" > "+ out_dir)

for sec in secs:
    if sec == "cfg":
        continue
    tran(sec)
