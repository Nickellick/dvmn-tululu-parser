import argparse
import os
import sys
import time

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
from urllib.parse import urljoin


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


def get_book_meta_info(page):
    book = {
                'author': None,
                'title': None
            }

    soup = BeautifulSoup(page, 'lxml')

    title, author = soup.find('td', class_='ow_px_td')\
        .find('h1').text.split('::')
    book['title'] = title.strip()
    book['author'] = author.strip()

    return book


def get_book_cover_link(page):
    soup = BeautifulSoup(page, 'lxml')
    img_rel_link = soup.find('div', class_='bookimage').find('img')['src']
    img_abs_link = urljoin('https://tululu.org/', img_rel_link)
    return img_abs_link


def get_comments(page):
    soup = BeautifulSoup(page, 'lxml')
    comments = []
    raw_comments = soup.find_all('div', class_='texts')
    for raw_comment in raw_comments:
        comment = {}
        author = raw_comment.find('b').text
        text = raw_comment.find('span', class_='black').text
        comment['author'] = author
        comment['text'] = text
        comments.append(comment)
    return comments


def get_genres(page):
    soup = BeautifulSoup(page, 'lxml')
    genres = []
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    for raw_genre in raw_genres:
        genres.append(raw_genre.text)
    return genres


def print_genres(url):
    response = requests.get(url)
    response.raise_for_status()

    print(get_genres(response))


def download_comments(url, filename, folder='comments/'):
    response = requests.get(url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    path = f'{os.path.join(folder, sanitize_filename(filename))}'

    comments = get_comments(response)

    with open(path, 'w') as commentfile:
        for comment in comments:
            commentfile.write(f'Author: {comment["author"]}\n')
            commentfile.write(f'Text: {comment["text"]}\n\n')

    return path


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    path = f'{os.path.join(folder, sanitize_filename(filename))}'

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
    book = {}
    book['genres'] = get_genres(page)
    book['comments'] = get_comments(page)
    book_meta = get_book_meta_info(page)
    book['author'] = book_meta['author']
    book['title'] = book_meta['title']
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
        print(f'Author: {book_meta["author"]}')
        print(f'Title: {book_meta["title"]}')
        print(f'Genres: {", ".join(book_meta["genres"])}')
        print(f'Comments: {book_meta["comments"]}')
        print('\n\n')


if __name__ == '__main__':
    main()
