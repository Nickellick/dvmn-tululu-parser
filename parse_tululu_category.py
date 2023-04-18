import argparse
import json
import sys

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

from tululu import download_book, get_html
from tululu import handle_connection


def init_argparse():
    parser = argparse.ArgumentParser(description='Tululu.org parser')
    parser.add_argument('--start_page', type=int, help='Start book page')
    parser.add_argument('--end_page', type=int, help='Stop book page'
                        '(excluding)')
    parser.add_argument('--dest_folder', type=str, help='Destination folder')
    parser.add_argument('--skip_imgs', help='Skip book cover download)')
    parser.add_argument('--skip_txt', help='Skip book cover download)')
    return parser.parse_args()


@handle_connection
def get_books_from_page(base_url, url, **kwargs):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    books_selector = '.d_book'
    link_selector = 'a'
    rel_links = [book.select_one(link_selector)['href']
                 for book in soup.select(books_selector)]
    abs_links = [urljoin(base_url, rel_link)
                 for rel_link in rel_links]
    return abs_links


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
    jsons = {}
    for page_num in range(start_page, end_page):
        if page_num == 1:
            url = category_url
        else:
            url = urljoin(category_url, f'{page_num}')
        abs_links = get_books_from_page(base_url, url,
                                        con_error_message='Error while '
                                        'fetching category page '
                                        f'#{page_num}!\n'
                                        'Can\'t reach server. Trying again...',
                                        http_error_message='Error while '
                                        f'fetching category page #{page_num}!'
                                        '\n Page does not exists. '
                                        'Skipping...',)
        if not abs_links:
            continue
        for link in abs_links:
            print(link)
            book_id = link.split('/')[-2][1::]
            txt_url = urljoin(base_url, 'txt.php')
            params = {
                'id': book_id
            }
            prep_req = requests.models.PreparedRequest()
            prep_req.prepare_url(txt_url, params)
            dl_txt_link = prep_req.url
            book = download_book(link, dl_txt_link, book_id,
                                 con_error_message='Error! Can\'t reach '
                                 'server. Trying again...',
                                 http_error_message='Error! Can\'t find book '
                                 f'with id {book_id}\n\n'
                                 )
            if not book:
                continue

            jsons[book_id] = book['comments']
            print(f'Succesfully downloaded book #{book_id}')

    with open('comments.json', 'w', encoding='utf-8') as commentfile:
        json.dump(jsons, commentfile, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
