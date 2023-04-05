import argparse
import json
import os
import sys
import time

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

from tululu import download_image, download_txt, get_html, parse_book_page


def init_argparse():
    parser = argparse.ArgumentParser(description='Tululu.org parser')
    parser.add_argument('--start_page', type=int, help='Start book page')
    parser.add_argument('--end_page', type=int, help='Stop book page (excluding)')
    return parser.parse_args()


def main():
    last_page = 701
    args = init_argparse()
    if not args.start_page:
        print('Start id is not specified', file=sys.stderr)
        exit(1)
    start_page = args.start_page
    if not args.end_page:
        end_page = last_page + 1
    else:
        end_page = args.end_page
    base_url = 'https://tululu.org/'
    category_url = urljoin(base_url, 'l55/')
    for page_num in range(start_page, end_page):
        page_exists = True
        while True:
            try:
                if page_num == 1:
                    html = get_html(category_url)
                else:
                    html = get_html(urljoin(category_url, f'{page_num}'))
                soup = BeautifulSoup(html, 'lxml')
                books_selector = '.d_book'
                link_selector = 'a'
                rel_links = [i.select_one(link_selector)['href']
                             for i in soup.select(books_selector)]
                abs_links = [urljoin(base_url, rel_link)
                             for rel_link in rel_links]
                break
            except requests.exceptions.ConnectionError:
                print(
                    f'Error while fetching category page #{page_num}!\n'\
                    'Can\'t reach server. Trying again...',
                    file=sys.stderr
                )
                time.sleep(5)
                continue
            except requests.exceptions.HTTPError:
                print(
                    f'Error while fetching category page #{page_num}!\n'\
                    'Page does not exists. Skipping...',
                    file=sys.stderr
                )
                page_exists = False
                break
        if not page_exists:
            continue
        for link in abs_links:
            id_exists = True
            book_id = link.split('/')[-2][1::]
            txt_url = urljoin(base_url, 'txt.php')
            params = {
                'id': book_id
            }
            prep_req = requests.models.PreparedRequest()
            prep_req.prepare_url(txt_url, params)
            dl_txt_link = prep_req.url
            while True:
                try:
                    page = get_html(link)
                    book = parse_book_page(link, page)
                    download_txt(dl_txt_link, f'{book_id}. {book["title"]}')
                    download_image(book['cover'], str(book_id))
                    break
                except requests.exceptions.ConnectionError:
                    print(
                        f'Error while fetching book #{book_id}!\n'
                        'Can\'t reach server. Trying again...',
                        file=sys.stderr
                    )
                    time.sleep(5)
                    continue
                except requests.HTTPError:
                    print(
                        f'Error while fetching book #{book_id}!\n'
                        'Book does not exists. Skipping...',
                        file=sys.stderr
                    )
                    id_exists = False
                    break
            if not id_exists:
                continue
            book.pop('cover')
            json_folder = 'json'
            os.makedirs(json_folder, exist_ok=True)
            path = os.path.join(json_folder, f'{book_id}.json')
            with open(path, 'w', encoding='utf-8') as bookfile:
                json.dump(book, bookfile, ensure_ascii=False, indent=2)
            print(f'Succesfully downloaded book #{book_id}')

if __name__ == '__main__':
    main()
