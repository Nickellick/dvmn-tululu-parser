import json
import math
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from urllib.parse import quote


def load_template(path='template.html'):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    return env.get_template(path)


def localize_book_cover(books, path='../result/covers'):
    for book in books:
        ext = book['cover'].split('.')[-1]
        book['cover'] = quote(os.path.join(path, f'{book["id"]}.{ext}'))
        book['alt'] = f'{book["author"]} {book["title"]}'


def add_text_link(books, path='../result/books/'):
    for book in books:
        book['text'] = quote(os.path.join(
            path,
            f'{book["id"]}. {book["title"]}.txt'
        ))


def on_reload(books):
    books_per_page = 20
    template = load_template()
    books_paged = chunked(books, books_per_page)
    total_pages = math.ceil(len(books) / books_per_page)
    for i, books_page in enumerate(books_paged):
        if i == 0:
            pages = [1, 2, 3]
            paginator_selector = 0
        elif i == total_pages - 1:
            pages = [total_pages - 2, total_pages - 1, total_pages]
            paginator_selector = 2
        else:
            pages = [i, i+1, i+2]
            paginator_selector = 3
        rel_page_links = [f'/pages/index{page}.html' for page in pages]
        rendered_page = template.render(
            book_chunks=chunked(books_page, 2), 
            rel_page_links=rel_page_links,
            paginator_selector=paginator_selector,
            pages=pages
        )
        os.makedirs('pages', exist_ok=True)
        with open(os.path.join('pages', f'index{i+1}.html'), 'w',
                  encoding='utf8') as file:
            file.write(rendered_page)


def main():
    books = {}
    with open('result/books.json', 'r') as file:
        books = json.load(file)
    localize_book_cover(books)
    add_text_link(books)
    server = Server()
    on_reload(books)
    server.watch('template.html', lambda: on_reload(books))
    server.serve(root='.', default_filename='pages/index1.html')



if __name__ == '__main__':
    main()        
