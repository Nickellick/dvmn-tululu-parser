import os

from bs4 import BeautifulSoup
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


def book_meta_info(book_id):
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


def main():
    try:
        meta = book_meta_info(1)
        print(f'Заголовок: {meta["title"]}')
        print(f'Автор: {meta["author"]}')
    except requests.HTTPError:
        pass

if __name__ == '__main__':
    main()