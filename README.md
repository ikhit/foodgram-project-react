# Foodgram - Социальная сеть для публикации рецептов

Foodgram - это веб-платформа, которая позволяет пользователям создавать, просматривать и обмениваться рецептами кулинарных блюд. Сервис предоставляет возможность подписываться на интересных авторов, добавлять понравившиеся рецепты в избранное, а также формировать продуктовую корзину для упрощения процесса покупки необходимых ингредиентов. Проект доступен по ссылке - [Foodgram](https://megafoodgram.servebeer.com)

## Основные функции

- **Публикация рецептов**: Пользователи могут делиться своими кулинарными шедеврами, указывая ингредиенты, этапы приготовления и фотографии готовых блюд.
- **Поиск рецептов**: Продвинутый поиск по названиям, тегам и ингредиентам поможет найти идеальный рецепт.
- **Подписки на авторов**: Оставайтесь в курсе новинок от ваших любимых авторов благодаря удобной системе подписок.
- **Избранное**: Сохраняйте понравившиеся рецепты в избранное, чтобы возвращаться к ним в любое время.
- **Продуктовая корзина**: Добавляйте рецепты в продуктовую корзину, чтобы сформировать полный список ингредиентов для покупки.

## Технологический стек

- **Frontend**: React
- **Backend**: Python, Django REST Framework, PostgreSQL, Docker, GitHub Actions, Nginx

## Локальное развертывание проекта

- Клонировать репозиторий: 

```
git clone git@github.com:ikhit/foodgram-project-react.git
```

- Перейти в директорию проекта.

- Создать .env файл:

```
touch .env
```

- Заполнить .env файл данными:

```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=db
DB_PORT=5432
DJANGO_SETTINGS_SECRET_KEY=
DJANGO_DEBUG_STATUS=True 
DJANGO_SETTINGS_ALLOWED_HOSTS=127.0.0.1, foodgram.example.fake.com, localhost
```

Выполнить команду:

```
docker compose up --build
```

Выполнить миграции:

```
docker compose exec backend python manage.py migrate
```

Собрать статику:

```
docker compose exec backend python manage.py collectstatic
```

Заполнить базу данных ингредиентами и тегами:

```
docker compose exec backend python manage.py upload_data
```

Проект будет развернут локально по адресу **127.0.0.1**

## Автор

- **Игорь Хитрик** - [ikhit](https://github.com/ikhit)