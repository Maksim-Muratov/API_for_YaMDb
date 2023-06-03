# api_yamdb

## Проект YaMDb собирает отзывы пользователей на произведения.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Reagent992/api_yamdb.git
```

```
cd api_yamdb
```

Создать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Как импортировать данные из scv в базу данных:

Перейдите в shell:

```
python3 manage.py shell
```

Импортируйте скрипт:

```
from static.data.import_data import import_data
```

Запустите скрипт:

* с отчетом об ошибках `import_data(True)`

* без отчета `import_data()`

### Авторы:

* Кунгурова Ксения
* Садыков Мирон
* Муратов Максим
