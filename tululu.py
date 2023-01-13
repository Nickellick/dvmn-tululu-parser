import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
from urllib.parse import urljoin

def check_for_redirect(checked_response):
    for response in checked_response.history:
        if response.status_code >= 300 and response.status_code < 400:
            raise requests.HTTPError("Redirect! Probably book is not available")


def download_book(book_id):
    url = 'https://tululu.org/txt.php'
    

    check_book_for_exist(book_id)
    
    meta_info = get_book_meta_info(book_id)
    filename = f'{book_id}. {meta_info["title"]}'
    return download_txt(build_book_url(), filename)

def get_book_meta_info(book_id):
    url = f'https://tululu.org/b{book_id}'

    book_meta = {
                'author': None,
                'title': None
            }

    soup = BeautifulSoup(get_book_html(book_id), 'lxml')

    title, author = soup.find('td', class_='ow_px_td').find('h1').text.split('::')
    book_meta['title'] = title.strip()
    book_meta['author'] = author.strip()

    return book_meta

def get_book_html(book_id):
    check_book_for_exist(book_id)
    url = f'https://tululu.org/b{book_id}'

    response = requests.get(url)
    response.raise_for_status()

    return response.text


def build_book_url(book_id):
    url = 'https://tululu.org/txt.php'
    

    params = {
                'id': book_id
            }
    
    prereq = requests.models.PreparedRequest()
    prereq.prepare_url(url, params)

    return prereq.url


def check_book_for_exist(book_id):
    response = requests.get(build_book_url(book_id))
    response.raise_for_status()
    check_for_redirect(response)

def get_book_cover_link(book_id):
    soup = BeautifulSoup(get_book_html(book_id), 'lxml')

    img_rel_link = soup.find('div', class_='bookimage').find('img')['src']
    img_abs_link = urljoin('https://tululu.org/', img_rel_link)
    return img_abs_link

def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)

    path = f'{os.path.join(folder, sanitize_filename(filename))}.txt'

    with open(path, 'wb') as bookfile:
        bookfile.write(response.content)
    
    return path


def main():
    book_ids = [_ for _ in range(1, 11)]

    for book_id in book_ids:
        try:
            print(get_book_cover_link(book_id))
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    main()