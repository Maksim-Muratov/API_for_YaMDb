# Командная разработка API для YaMDb

### Описание проекта
YaMDb - база данных отзывов пользователей о фильмах, книгах и музыке. В команде из 3-х разработчиков, опираясь на ТЗ, реализовывали API для этого проекта.

Я реализовал всё, что связано с отзывами, комментариями и рейтингом произведений.

### Как локально развернуть проект?
- Клонируйте репозиторий
- Создайте и активируйте виртуальное окружение
- Установите все необходимые пакеты из requirements.txt
- Выполните миграции
- Запустите сервер

### Как импортировать данные из scv в базу данных?

- Перейдите в shell
```
python3 manage.py shell
```

- Импортируйте скрипт
```
from static.data.import_data import import_data
```

- Запустите скрипт
```
import_data(True)
```

### Авторы:

- Муратов Максим
- Садыков Мирон
- Кунгурова Ксения
