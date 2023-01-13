import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests

def check_for_redirect(checked_response):
    for response in checked_response.history:
        if response.status_code >= 300 and response.status_code < 400:
            raise requests.HTTPError("Redirect! Probably book is not available")


def download_book(book_id):
    url = 'https://tululu.org/txt.php'
    

    params = {
                'id': book_id
            }
    
    prereq = requests.models.PreparedRequest()
    prereq.prepare_url(url, params)

    full_url = prereq.url

    # Checking is file exists
    response = requests.get(full_url)
    response.raise_for_status()
    check_for_redirect(response)
    
    meta_info = get_book_meta_info(book_id)
    filename = f'{book_id}. {meta_info["title"]}'
    return download_txt(full_url, filename)

def get_book_meta_info(book_id):
    url = f'https://tululu.org/b{book_id}'

    book_meta = {
                'author': None,
                'title': None
            }
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    title, author = soup.find('td', class_='ow_px_td').find('h1').text.split('::')
    book_meta['title'] = title.strip()
    book_meta['author'] = author.strip()

    return book_meta


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
            download_book(book_id)
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    main()