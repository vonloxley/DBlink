from os import path
import bs4
import cloudscraper
from airium import Airium

PBASE_URL = 'https://www.blinkist.com'

def scrape(url: str):
    scraper = cloudscraper.create_scraper()
    return scraper.get(url)

def pbookpage(html: bs4.BeautifulSoup):
    title:str = html.find('a', {'class':'share__facebook-icon'})['data-title']
    for ha1 in html.find_all('h1'):
        ha1.name='h2'
    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang="de"):
        with a.head():
            with a.title():
                a(title)
            with a.style():
                a('p {width: 80ex; line-height: 1.3; font-size: 120%;} p')
        with a.body():
            with a.h1():
                a(title)
            for d in html('div'):
                try:
                    if 'chapter' in d['class']:
                        a(d)
                except KeyError:
                    None
    with open(path.normpath('out/'+"".join(x for x in title if x.isalnum())+'.html'),'wt') as f:
        f.write(str(a))

def pstartpage(html: bs4.BeautifulSoup):
    for a in html('a'):
        try:
            if 'cta' in a['class']:
                pbookpage(bs4.BeautifulSoup(scrape(PBASE_URL + a['href']).text, 'html.parser'))
        except KeyError:
                None

def get_blink(url: str):
    blink = scrape(url)
    html = bs4.BeautifulSoup(blink.text, 'html.parser')
    
    pstartpage(html)

def main():
    get_blink('https://www.blinkist.com/de/nc/daily')
    get_blink('https://www.blinkist.com/en/nc/daily')

if __name__ == '__main__':
    main()
