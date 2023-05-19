import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def load_template(path='template.html'):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    return env.get_template(path)


def localize_book_cover(books, path='result/covers'):
    for book in books:
        ext = book['cover'].split('.')[-1]
        book['cover'] = os.path.join(path, f'{book["id"]}.{ext}')
        book['alt'] = f'{book["author"]} {book["title"]}'


def on_reload(books):
    template = load_template()
    rendered_page = template.render(
        book_chunks=chunked(books, 2)
    )
    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


def main():
    books = {}
    with open('result/books.json', 'r') as file:
        books = json.load(file)
    localize_book_cover(books)
    server = Server()
    on_reload(books)
    server.watch('template.html', lambda: on_reload(books))
    server.serve(root='.')


if __name__ == '__main__':
    main()        
