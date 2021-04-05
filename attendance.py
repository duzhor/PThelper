import json
import re
import time

import requests
import yaml
from bs4 import BeautifulSoup


SITES = {
    'chdbits': ['https://chdbits.co/index.php', None],
    'hdchina': ['https://hdchina.org/index.php', 'https://hdchina.org/plugin_sign-in.php?cmd=signin'],
    'totheglory': ['https://totheglory.im/index.php', None],
    'hdsky': ['https://hdsky.me/index.php', None],
    'mteam': ['https://kp.m-team.cc/index.php', None],

    'springsunday': ['https://springsunday.net/index.php', None],
    'ourbits': ['https://www.ourbits.club/index.php', None],
    'hdhome': ['https://hdhome.org/index.php', 'https://hdhome.org/attendance.php'],

    'open': ['https://open.cd/index.php', 'https://open.cd/plugin_sign-in.php?cmd=signin'],
    'dicmusic': ['https://dicmusic.club/index.php', None],
    'soulvoice': ['https://pt.soulvoice.club/index.php', None],

    'dmhy': ['http://u2.dmhy.org/index.php', None],
    'lemonhd': ['https://lemonhd.org/index.php', 'https://lemonhd.org/attendance.php'],

    'pthome': ['https://pthome.net/index.php', None],
    'btschool': ['https://pt.btschool.club/index.php', 'https://pt.btschool.club/index.php?action=addbonus'],
    'hdarea': ['https://www.hdarea.co/index.php', 'https://www.hdarea.co/sign_in.php'],

    'haidan': ['https://www.haidan.video/index.php', 'https://www.haidan.video/signin.php'],
}


def align(string, length=20):
    str_len = 0
    for _ in string:
        code = ord(_)
        if code <= 126:
            str_len += 1
        else:
            str_len += 2
    return string + ' ' * (length - str_len)


class CheckIn(object):

    def __init__(self, site, cookie):
        self.site = site
        self.index_url, self.signin_url = SITES[site]
        headers = {
            'accept-encoding': 'gzip',
            'accept-language': 'zh-CN,en,*',
            'cookie': cookie,
            'referer': self.index_url,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
            # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
        }

        self.session = requests.Session()
        self.session.headers.update(headers)

    @property
    def un_check_in(self):
        return '<该站点无需签到，访问首页>'

    @property
    def time_now(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def message(self, msg, info=''):
        msg = self.site + ': ' + msg
        return ' '.join([self.time_now, '|', align(msg, 55), '|', info])

    def check_in(func):
        # from functools import wraps
        #
        # @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                day_bonus = func(self, *args, **kwargs)
                info = self.info_block()
            except Exception as e:
                msg = self.message(str(e))
            else:
                msg = self.message(day_bonus, info)
            return msg

        return wrapper

    def soup(self, url):
        r = self.session.get(url)
        with self.session.get(url) as r:
            soup = BeautifulSoup(r.text, 'lxml')
            return soup

    def info_block(self):
        soup = self.soup(self.index_url)
        info = soup.find('span', attrs={'class': 'medium'}).text
        return ' '.join(info.split())

    def hdchina(self):
        r = self.session.get(self.index_url)
        csrf = re.findall(r'logout.php\?csrf=(\w+)', r.text)[0]
        r_ = self.session.post(self.signin_url, data={'csrf': csrf})
        result = r_.json()
        return result

    @check_in
    def totheglory(self):
        return self.un_check_in

    @check_in
    def hdsky(self):
        return self.un_check_in

    @check_in
    def mteam(self):
        return self.un_check_in

    @check_in
    def springsunday(self):
        return self.un_check_in

    @check_in
    def ourbits(self):
        return self.un_check_in

    @check_in
    def hdhome(self):
        soup = self.soup(self.signin_url)
        result = soup.find_all('td')[-1].text.strip()
        return result

    @check_in
    def open(self):
        return self.un_check_in

    @check_in
    def dicmusic(self):
        return self.un_check_in

    @check_in
    def soulvoice(self):
        return self.un_check_in

    @check_in
    def dmhy(self):
        return self.un_check_in

    @check_in
    def lemonhd(self):
        soup = self.soup(self.signin_url)
        result = soup.find('span', attrs={'id': 'dayBonusAvgId'}).text
        return result

    @check_in
    def pthome(self):
        return self.un_check_in

    @check_in
    def btschool(self):
        soup = self.soup(self.signin_url)
        result = soup.find('font', attrs={'color': 'white'})
        result_ = result.text if result else str(result)
        return result_

    @check_in
    def hdarea(self):
        r = self.session.post(self.signin_url, data={'action': 'sign_in'})
        result = r.text
        return result

    def haidan(self):
        try:
            self.session.get(self.signin_url)
            soup = self.soup(self.index_url)
            day_bonus = soup.find('div', attrs={'class': 'modal-body'}).text.strip()
            info_list = soup.find_all('div', attrs={'class': 'userinfo-half'})
            info = ''.join([' '.join(_.text.split()) for _ in info_list])
            info = re.sub('×.*!|&nbsp', '', info)
        except Exception as e:
            msg = self.message(str(e))
        else:
            msg = self.message(day_bonus, info)
        return msg


def check_yaml():
    confile = 'config.yaml'
    with open(confile, 'r', encoding='utf8') as f:
        try:
            conf = yaml.safe_load(f)
        except Exception as e:
            print(e, 'Config file is invalid YAML')
            raise yaml.YAMLError
        else:
            return conf


class Push(object):

    def __init__(self, msg):
        self.content = self.template(msg)

    def pushplus(self, token):
        content = json.dumps(self.content, ensure_ascii=False)
        url = 'http://pushplus.hxtrip.com/send'
        data = {
            "token": token,
            "title": "PT站签到工具",
            "content": content,
            "template": "json"
        }
        with requests.post(url, data=data) as r:
            result = r.json()
            print(result)

    @classmethod
    def template(cls, data):
        result = [_.split('|')[1].replace(' ', '').split(':') for _ in data]
        return dict(result)


def main():
    message = list()

    config = check_yaml()
    token = config.pop('TOKEN')
    for s in SITES:
        s = s.lower().replace('-', '')
        cookies = config.get(s)
        if cookies:
            ci = CheckIn(s, cookies)
            msg = getattr(ci, s)()

            message.append(msg)
            print(msg)

    Push(message).pushplus(token)


if __name__ == '__main__':
    main()
    input('DONE. Press ENTER to close it.')
