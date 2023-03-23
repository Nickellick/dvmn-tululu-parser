import argparse
import os
import sys
import time

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
from urllib.parse import urljoin, urlparse


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
    title, author = page_soup.find('td', class_='ow_px_td')\
        .find('h1').text.split('::')
    title = title.strip()
    author = author.strip()

    return title, author


def get_book_cover_link(page_soup):
    img_rel_link = page_soup.find('div', class_='bookimage').find('img')['src']
    img_abs_link = urljoin('https://tululu.org/', img_rel_link)
    return img_abs_link


def get_comments(page_soup):
    comments = []
    raw_comments = page_soup.find_all('div', class_='texts')
    for raw_comment in raw_comments:
        comment = {}
        author = raw_comment.find('b').text
        text = raw_comment.find('span', class_='black').text
        comment['author'] = author
        comment['text'] = text
        comments.append(comment)
    return comments


def get_genres(page_soup):
    genres = [genre.text
              for genre in
              page_soup.find('span', class_='d_book').find_all('a')]
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

    os.makedirs(folder, exist_ok=True)

    path = f'{os.path.join(folder, sanitize_filename(filename))}.txt'

    with open(path, 'wb') as bookfile:
        bookfile.write(response.content)

    return path


def parse_book_page(page):
    page_soup = BeautifulSoup(page, 'lxml')
    title, author = get_book(page_soup)
    book = {
        'genres': get_genres(page_soup),
        'comments': get_comments(page_soup),
        'cover': get_book_cover_link(page_soup),
        'author': author,
        'title': title
    }
    return book


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    return response.text


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    args = init_argparse()
    for book_id in range(args.start_id, args.end_id + 1):
        id_exists = True
        url = f'https://tululu.org/b{book_id}/'

        while True:
            try:
                page = get_html(url)
                break
            except requests.exceptions.ConnectionError:
                eprint('Error! Can\'t reach server. Trying again...')
                time.sleep(5)
                continue
            except requests.HTTPError:
                eprint(f'Error! Can\'t find book with id {book_id}\n\n')
                id_exists = False
                break
        if not id_exists:
            continue
        
        book = parse_book_page(page)
        download_txt(url, f'{book_id}. {book["title"]}')
        download_image(book['cover'], str(book_id))
        print(f'Author: {book["author"]}')
        print(f'Title: {book["title"]}')
        print(f'Genres: {", ".join(book["genres"])}')
        print(f'Comments: {book["comments"]}')
        print('\n\n')


if __name__ == '__main__':
    main()
