import argparse
import os
import sys
import time

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
from urllib.parse import urljoin, urlparse


def handle_connection(func):
    def wrapper(*args, **kwargs):
        print(kwargs.keys())
        con_error_message = kwargs.pop('con_error_message')
        http_error_message = kwargs.pop('http_error_message')
        result = None
        while True:
            try:
                result = func(*args, **kwargs)
                break
            except requests.exceptions.ConnectionError:
                print(con_error_message, file=sys.stderr)
                time.sleep(5)
                continue
            except requests.exceptions.HTTPError:
                print(http_error_message)
                break
        return result
    return wrapper


def init_argparse():
    parser = argparse.ArgumentParser(description='Tululu.org parser')
    parser.add_argument('start_id', type=int, help='Start book id')
    parser.add_argument('end_id', type=int, help='Stop book id (including)')
    return parser.parse_args()


def check_for_redirect(checked_response):
    if checked_response.history:
        raise requests.HTTPError(
            "Redirect! Probably book is not available"
            )


def get_book(page_soup):
    selector = '.ow_px_td h1'
    title, author = page_soup.select_one(selector)\
        .text.split('::')
    title = title.strip()
    author = author.strip()

    return title, author


def get_book_cover_link(book_url, page_soup):
    selector = '.bookimage img'
    img_rel_link = page_soup.select_one(selector)['src']
    img_abs_link = urljoin(book_url, img_rel_link)
    return img_abs_link


def get_comments(page_soup):
    comments = []
    comments_selector = '.texts'
    author_selector = 'b'
    text_selector = '.black'
    raw_comments = page_soup.select(comments_selector)
    for raw_comment in raw_comments:
        comment = {}
        author = raw_comment.select_one(author_selector).text
        text = raw_comment.select_one(text_selector).text
        comment['author'] = author
        comment['text'] = text
        comments.append(comment)
    return comments


def get_genres(page_soup):
    book_selector = 'span.d_book'
    genre_selector = 'a'
    genres = [genre.text
              for genre in
              page_soup.select_one(book_selector).select(genre_selector)]
    return genres


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    img_rel_path = urlparse(url).path
    img_ext = os.path.splitext(img_rel_path)[1]

    path = f'{os.path.join(folder, sanitize_filename(filename) + img_ext)}'

    with open(path, 'wb') as imgfile:
        imgfile.write(response.content)

    return path


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)

    path = f'{os.path.join(folder, sanitize_filename(filename))}.txt'

    with open(path, 'wb') as bookfile:
        bookfile.write(response.content)

    return path


def parse_book_page(base_url, page):
    page_soup = BeautifulSoup(page, 'lxml')
    title, author = get_book(page_soup)
    book = {
        'genres': get_genres(page_soup),
        'comments': get_comments(page_soup),
        'cover': get_book_cover_link(base_url, page_soup),
        'author': author,
        'title': title
    }
    return book


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    return response.text


@handle_connection
def download_book(book_url, txt_url, book_id,
                  **kwargs):
    page = get_html(book_url)
    book = parse_book_page(book_url, page)
    download_txt(txt_url, f'{book_id}. {book["title"]}')
    download_image(book['cover'], str(book_id))
    return book


def main():
    args = init_argparse()
    base_url = 'https://tululu.org/'
    for book_id in range(args.start_id, args.end_id + 1):
        url = urljoin(base_url, f'/b{book_id}/')
        txt_url = urljoin(base_url, 'txt.php')
        params = {
            'id': book_id
        }
        prep_req = requests.models.PreparedRequest()
        prep_req.prepare_url(txt_url, params)
        dl_txt_link = prep_req.url
        book = download_book(url, dl_txt_link, book_id,
                             con_error_message='Error! Can\'t reach '
                             'server. Trying again...',
                             http_error_message='Error! Can\'t find book '
                             f'with id {book_id}\n\n'
                             )
        if not book:
            continue

        print(f'Author: {book["author"]}')
        print(f'Title: {book["title"]}')
        print(f'Genres: {", ".join(book["genres"])}')
        print(f'Comments: {book["comments"]}')
        print('\n\n')


if __name__ == '__main__':
    main()
