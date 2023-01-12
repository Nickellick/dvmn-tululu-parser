import os

import requests


def download_txt_book(book_id):
    url = "https://tululu.org/txt.php"

    params = {
                'id': book_id
            }
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.content


def save_book(path, book_binary):
    with open(path, 'wb') as book_file:
            book_file.write(book_binary)


def main():
    book_dir = 'books'
    book_ids = [i for i in range(1, 11)]
    os.makedirs(book_dir, exist_ok=True)
    for book_id in book_ids:
        save_book(os.path.join(book_dir, f'id{book_id}.txt'), download_txt_book(book_id))


if __name__ == '__main__':
    main()