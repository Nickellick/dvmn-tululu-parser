from bs4 import BeautifulSoup
from urllib.parse import urljoin

from tululu import get_html


def main():
    category_url = 'https://tululu.org/l55/'
    for page_num in range(1, 11):
        if page_num == 1:
            html = get_html(category_url)
        else:
            html = get_html(urljoin(category_url, f'{page_num}'))
        soup = BeautifulSoup(html, 'lxml')
        rel_links = [i.find('a')['href']
                     for i in soup.find_all('table', class_='d_book')]
        abs_links = [urljoin('https://tululu.org', rel_link)
                     for rel_link in rel_links]
        for link in abs_links:
            print(link)


if __name__ == '__main__':
    main()
