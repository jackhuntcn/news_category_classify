#-*- coding:utf8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
logging.basicConfig(filename='chinanews.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
import time
import requests
from bs4 import BeautifulSoup
import redis
from datetime import datetime, timedelta

cli = redis.Redis()

def fetch_oneday(whichday):
    try:
        year, month_day = whichday.split('-')
    except:
        return None
    base_url = "http://www.chinanews.com/scroll-news/%s/%s/news.shtml" % (year, month_day)
    try:
        resp = requests.get(base_url, timeout=10)
        resp.encoding = "gbk"
        soup = BeautifulSoup(resp.text, "html.parser")
        content = soup.find('div', class_='content_list')
        li = content.find_all("li")
        cnt = 0
        for item in li:
            try:
                category = item.find('div', class_='dd_lm').text.replace(r'[', '').replace(r']', '')
                title = item.find('div', class_='dd_bt').text
                href = item.find('div', class_='dd_bt').a.attrs['href']
                di = {'category':category, 'title':title}
                if not cli.hget('chinanews', href):
                    cli.hset('chinanews', href, str(di))
                    cnt += 1
            except:
                continue
        print "%s/%s stored %d news" % (year, month_day, cnt)
    except:
        logging.error("failed on getting urls from %s" % base_url)
        return None

if __name__ == "__main__":
    today = datetime.today()
    for i in range(1, 1500):
        whichday = (today - timedelta(days=i)).strftime("%Y-%m%d")
        fetch_oneday(whichday)
        time.sleep(1)

