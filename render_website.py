import json
import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

books = {}

with open('result/books.json', 'r') as file:
    books = json.load(file)

for book in books:
    ext = book['cover'].split('.')[-1]
    book['cover'] = f'result/covers/{book["id"]}.{ext}'


rendered_page = template.render(
    books=books
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)
