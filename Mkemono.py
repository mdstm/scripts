'''下载 kemono 上的图片，需要提供运行中的网页文件'''

import argparse
import asyncio
from glob import iglob
import os
import re

from bs4 import BeautifulSoup

from util.Madown import AsyncDownloader
from util.Mfile import normalizeName


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'referer': 'https://kemono.su/',
}

# 目录格式
dir_format = '{user}`{site}`{uid}/{date}`{site}`{uid}`{pid}`{title}/'.format


def find_info(html: str) -> tuple[str, list[str]]:
    '''从网页中获取信息，返回下载目录和图片链接'''

    soup = BeautifulSoup(html, 'lxml')
    a = soup.select_one('.post__user-name')
    site, uid = re.search(r'([^/]+)/user/([^/]+)', a.attrs['href'].strip())\
        .group(1, 2)
    user = normalizeName(re.sub(r'\s*\([^)]*\)$', '', a.text.strip()))
    pid = soup.select_one('meta[name="id"]').attrs['content'].strip()
    title = normalizeName(re.sub(r'\s*\([^)]*\)$', '',
        soup.select_one('.post__title span').text.strip()))
    date = soup.select_one('meta[name="published"]').attrs['content'].strip()
    date = ''.join((date[2:4], date[5:7], date[8:10])) # YYMMMDD
    urls = [a.attrs['href'].strip() for a in soup.select('.post__thumbnail a')]

    dir_name = dir_format(
        user=user, site=site, uid=uid, date=date, pid=pid, title=title,
    )
    return dir_name, urls


def add_html(adown: AsyncDownloader, html: str):
    '''将网页解析后加入下载队列中'''

    dir_name, urls = find_info(html)
    if not urls:
        return
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    name_fmt = str(len(str(len(urls) - 1))).join(('{}{:0', 'd}{}')).format
    for i, url in enumerate(urls):
        ext = url[url.rfind('.'):]
        name = name_fmt(dir_name, i, ext)
        adown.add(url, name)


async def kemono(html_name_pats: list[str]):
    '''创建下载器，读取文件中的网页并下载其中的图片'''

    async with AsyncDownloader(headers=HEADERS) as adown:
        for html_name_pat in html_name_pats:
            for html_name in iglob(html_name_pat):
                with open(html_name, 'r', encoding='utf-8') as f:
                    html = f.read()
                add_html(adown, html)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('html_file', nargs='+', help='kemono 网页文件')

    args = p.parse_args()

    asyncio.run(kemono(args.html_file))


if __name__ == '__main__':
    main()
