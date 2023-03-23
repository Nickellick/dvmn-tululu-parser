# Парсер книг с сайта [tululu.org](https://tululu.org)
Данный проект включает в себя
 - Набор функций для удобной работы с парсингом информации и скачиванием книг с сайта
 - Утилиту для полученя метаинформации о наборе книг

# Установка
Требуется установленный `Python 3.7` или новее. Скачать его можно [здесь](https://www.python.org/), или же в соответствующем репозитории для вашей ОС.
Для установки зависимостей используйте `pip` (или `pip3`, есть конфликт с `Python2`)
```
pip install -r requirements.txt
```

# Запуск
## Использование функций
Для использования функций для работы с [tululu.org](https://tululu.org/) достаточно импортировать пакет `tululu.py`
```py
import tululu
```
или
```py
from tululu import ...
```

## Использование утилиты
Чтобы использовать утилиту для получения метаданных о книге необходимо ввести следующую команду
```
python tululu.py <start_id> <end_id>
```
Ключи `start_id` и `end_id` являются обязательными, вводятся без скобок.
 - `start_id` - id, начиная с которого будет выводиться информация о книгах.
 - `end_id` - id последней выводимой книги (включительно).

Пример:
```
python tululu.py 20 30
```
выведет метаинформацию с 20 по 30 книги включительно.

# Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).