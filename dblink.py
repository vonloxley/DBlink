from os import path
from urllib.parse import urlparse

import bs4
import cloudscraper
from airium import Airium


def writetofile(apath: str, filename: str, extension: str, content: str) -> None:
    if not extension.startswith('.'):
        extension = '.' + extension
    filename = "".join(x for x in filename if x.isalnum())
    file = path.normpath(path.join(apath, filename) + extension)
    i = 1
    while (path.exists(file)):
        file = path.normpath(
            path.join(apath, filename + '-' + str(i) + extension))
        i += 1
    with open(file, 'wt') as f:
        f.write(content)


def scrape(url: str):
    scraper = cloudscraper.create_scraper()
    return scraper.get(url)


def pbookpage(html: bs4.BeautifulSoup, context):
    for ha1 in html.find_all('h1'):
        ha1.name = 'h2'
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="de"):
        with a.head():
            with a.title():
                a(context['title'])
            with a.style():
                a('p {width: 80ex; line-height: 1.3; font-size: 120%;}')
        with a.body():
            a(context['header'])
            for d in html('div'):
                try:
                    if 'chapter' in d['class']:
                        a(d)
                except KeyError:
                    pass

    writetofile('out', context['title'], 'html', str(a))


def pstartpage(html: bs4.BeautifulSoup, context):
    context['header'] = html.find('div', {'class': 'daily-book__header'})
    for ha3 in context['header'].find_all('h3'):
        ha3.name = 'h1'
    context['title'] = context['header'].find('h1').text
    for a in html('a'):
        try:
            if 'cta' in a['class']:
                pbookpage(bs4.BeautifulSoup(
                    scrape(context['BaseUrl'] + a['href']).text, 'html.parser'), context)
        except KeyError:
            pass


def get_blink(bookurl: str):
    context = {}
    up = urlparse(bookurl)
    context['BaseUrl'] = f'{up.scheme}://{up.netloc}'
    blink = scrape(bookurl)
    html = bs4.BeautifulSoup(blink.text, 'html.parser')

    pstartpage(html, context)


def main():
    get_blink('https://www.blinkist.com/de/nc/daily')
    get_blink('https://www.blinkist.com/en/nc/daily')


if __name__ == '__main__':
    main()
