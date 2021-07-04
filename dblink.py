import shelve
from datetime import date
from os import path
from urllib.parse import urlparse

import bs4
import cloudscraper
from airium import Airium


def writetofile(
        apath: str, filename: str, extension: str, content: str) -> None:
    """Write content to a new file. Filename will be constructed from
    filename and extension.
    If the file exists a number will be appended to filename.

    Args:
        apath (str): Filesystem path to the new file
        filename (str): Basename for the new file
        extension (str): Extesion of the new filename without dot
        content (str): Content to write into the file
    """
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
    """Caching generator for cloudscraper.
    Caches the html in `out/jar`. Uses url and todays date as the key.

    Args:
        url (str):  URL to fetch

    Returns:
        cloudscraper: An (cached) cloudscraper object
    """
    with shelve.open('out/jar') as jar:
        key = f'{url}-{str(date.today())}'
        if key in jar:
            scraper = jar[key]
        else:
            scraper = cloudscraper.create_scraper().get(url)
            jar[key] = scraper
    return scraper


def pbookpage(html: bs4.BeautifulSoup, context):
    """Parses the book page, generates and saves a simple html-file
    on `out/title.html`.

    Args:
        html (bs4.BeautifulSoup): BeautifulSoup object to parse
        context (dict): Parsercontext with title and header keys
    """
    style = '''p {
                width: 80ex;
                line-height: 1.3;
                font-size: 120%;
                hyphens: auto;}
            '''
    for tag in html.find_all():
        if tag.name == 'h1':
            tag.name = 'h2'
        del tag['style']

    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang=context['lang']):
        with a.head():
            with a.title():
                a(context['title'])
            with a.style():
                a(style)
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
    """Parse startpage

    Args:
        html (bs4.BeautifulSoup): BeautifulSooup object to parse
        context (dict): Parser context
    """
    context['header'] = html.find('div', {'class': 'daily-book__header'})
    for ha3 in context['header'].find_all('h3'):
        ha3.name = 'h1'
    context['title'] = context['header'].find('h1').text
    for a in html('a'):
        try:
            if 'cta' in a['class']:
                url = context['BaseUrl'] + a['href']
                pbookpage(
                    bs4.BeautifulSoup(
                        scrape(url).text, 'html.parser'
                    ), context
                )
        except KeyError:
            pass


def get_blink(bookurl: str, lang: str = 'de'):
    """Downloads a blink.

    Args:
        bookurl (str): Link to the startpage of the blink
    """
    context = {}
    up = urlparse(bookurl)
    context['BaseUrl'] = f'{up.scheme}://{up.netloc}'
    context['lang'] = lang
    blink = scrape(bookurl)
    html = bs4.BeautifulSoup(blink.text, 'html.parser')

    pstartpage(html, context)


def main():
    get_blink('https://www.blinkist.com/de/nc/daily', 'de')
    get_blink('https://www.blinkist.com/en/nc/daily', 'en')


if __name__ == '__main__':
    main()
