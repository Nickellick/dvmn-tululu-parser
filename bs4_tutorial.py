from bs4 import BeautifulSoup
import requests


url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
# Выводим HTML красиво
print(soup.prettify())

# Выводим содержимое первого попавшегося тега h1
print(soup.find('h1'))

# Ищем конкрентный тег
title_tag = soup.find('main').find('header').find('h1')
print(title_tag)

# Достаём оттуда текст
title_text = title_tag.text
print(title_text)

# Достаём картинку по классу
img_tag = soup.find('img', class_='attachment-post-image')
print(img_tag)

# Достаём ссылку на картинку
img_link = img_tag['src']
print(img_link)

# Достаём текст поста по классу
post_text = soup.find('div', class_='entry-content').text
print(post_text)

# Достаём текст поста по тегам
post_text = soup.find('main').find('article').find('div').text
print(post_text)
