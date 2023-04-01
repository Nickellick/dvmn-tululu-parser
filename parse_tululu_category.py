from bs4 import BeautifulSoup
from urllib.parse import urljoin

from tululu import get_html


def main():
    html = get_html('https://tululu.org/l55/')
    soup = BeautifulSoup(html, 'lxml')
    rel_link = soup.find('table', class_='d_book').find('a')['href']
    print(urljoin('https://tululu.org', rel_link))


if __name__ == '__main__':
    main()
