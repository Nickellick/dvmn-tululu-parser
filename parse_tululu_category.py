from bs4 import BeautifulSoup
from urllib.parse import urljoin

from tululu import get_html


def main():
    html = get_html('https://tululu.org/l55/')
    soup = BeautifulSoup(html, 'lxml')
    rel_links = [i.find('a')['href']
                 for i in soup.find_all('table', class_='d_book')]
    abs_links = [urljoin('https://tululu.org', rel_link)
                 for rel_link in rel_links]
    for link in abs_links:
        print(link)


if __name__ == '__main__':
    main()
