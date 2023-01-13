import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests

def check_for_redirect(checked_response):
    for response in checked_response.history:
        if response.status_code >= 300 and response.status_code < 400:
            raise requests.HTTPError("Redirect! Probably book is not available")


def download_txt_book(book_id):
    url = 'https://tululu.org/txt.php'

    params = {
                'id': book_id
            }
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)

    return response.content


def get_book_meta_info(book_id):
    url = f'https://tululu.org/b{book_id}'

    book_meta = {
                'author': None,
                'title': None
            }
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    title, author = soup.find('h1').text.split('::')
    book_meta['title'] = title.strip()
    book_meta['author'] = author.strip()

    return book_meta


def save_book(path, book_binary):
    with open(path, 'wb') as book_file:
            book_file.write(book_binary)

def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    os.makedirs(folder, exist_ok=True)

    path = f'{os.path.join(folder, sanitize_filename(filename))}.txt'

    with open(path, 'wb') as bookfile:
        bookfile.write(response.content)
    
    return path


def main():
    url = 'https://tululu.org/txt.php?id=1'

    filepath = download_txt(url, 'Алиби')
    print(filepath)  # Выведется books/Алиби.txt

    filepath = download_txt(url, 'Али/би', folder='books/')
    print(filepath)  # Выведется books/Алиби.txt

    filepath = download_txt(url, 'Али\\би', folder='txt/')
    print(filepath)  # Выведется txt/Алиби.txt

if __name__ == '__main__':
    main()