from xbmcswift2 import Plugin
from operator import itemgetter
from urlparse import urljoin

import subprocess, platform
import requests
import re
import os

from BeautifulSoup import BeautifulSoup as BS

plugin = Plugin()

BASE_URL = "http://sexfactor.com/episodes/"

@plugin.route('/')
def main_menu():
    items = show_episodes()
    return items

def show_episodes():
    r = requests.get(BASE_URL)
    
    soup = BS(r.text, convertEntities=BS.HTML_ENTITIES)
    
    episodes = soup.find('div', {'class': "episodes-list"})

    urls = [epi['href'] for epi in episodes.findAll('a')]
    labels = [epi.text for epi in episodes.findAll('div', {'class': 'info-line'})]
    thumbs = [urljoin(BASE_URL, epi['src']) for epi in episodes.findAll('img')]

    _its = zip(urls, labels, thumbs) 
    
    print thumbs

    items = [{'path': plugin.url_for('show_episode', url=i[0]), 'label': i[1], 'thumbnail': i[2]} for i in _its]

    return items

def __unpack_info(it):
    ptn = re.compile('"sources":\[\{"file":"(https:.+?\.mp4)"')
    url = ptn.findall(it['data-config'])[0].replace("\\","")
    title = it.text
    thumb = it.find('img')['src']

    if "http" not in thumb:
        thumb = urljoin(BASE_URL, thumb)

    return {'path': url, 'label': title, 'thumbnail': thumb, 'is_playable': True}

@plugin.route('/<url>')
def show_episode(url):    
    r = requests.get(url)

    soup = BS(r.text, convertEntities=BS.HTML_ENTITIES)
    
    materials = soup.find("div", {"class": "materials-list"})
    
    # get the main episode
    _its = [materials.find("div", {"class": "item active"})]
   
    # then the extras
    _its.extend(materials.findAll("div", {"class": "item "})) # watch for the extra space!
   
    items = [__unpack_info(i) for i in _its]
   
    return items


if __name__ == '__main__':
    plugin.run()
