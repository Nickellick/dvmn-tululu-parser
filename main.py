import os

import requests

book_ids = [i for i in range(1, 11)]

url = "https://tululu.org/txt.php"


os.makedirs('books', exist_ok=True)

for book_id in book_ids:
    params = {
        'id': book_id
    }
    response = requests.get(url, params=params)
    response.raise_for_status() 

    with open(f'books/id{book_id}.txt', 'wb') as book_file:
        book_file.write(response.content)