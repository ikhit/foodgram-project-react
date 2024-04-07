# flake8: noqa
image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
user_password = "1234"
user_email = "user@test.com"
create_data = {
    "ingredients": [{"id": 2, "amount": 30}, {"id": 3, "amount": 100}],
    "tags": [1],
    "image": image,
    "name": "Плов",
    "text": "Охапка дров и плов готов!",
    "cooking_time": 20,
}
updated_data = {
    "ingredients": [{"id": 1, "amount": 10}, {"id": 3, "amount": 20}],
    "tags": [1],
    "image": image,
    "name": "Жареный суп",
    "text": "Доработка рецепта от бати. Берегите обои!",
    "cooking_time": 40,
}
change_password_data = {
    "new_password": "Change_ME!",
    "current_password": user_password,
}

login_data = {"password": user_password, "email": user_email}

create_content_data = {
    "ingredients": [{"id": 2, "amount": 30}, {"id": 3, "amount": 100}],
    "tags": [1],
    "image": image,
    "name": "Плов",
    "text": "Охапка дров и плов готов!",
    "cooking_time": 20,
}

expected_recipe_data = {
    "id": 1,
    "ingredients": [
        {
            "id": 2,
            "name": "вроде бы мясо",
            "amount": 30,
            "measurement_unit": "г",
        },
        {
            "id": 3,
            "name": "вроде бы не мясо",
            "amount": 100,
            "measurement_unit": "г",
        },
    ],
    "tags": [{"id": 1, "name": "Обед", "color": "#32CD32", "slug": "lunch"}],
    "is_favorited": False,
    "is_in_shopping_cart": False,
    "image": "http://testserver/media/recipes/images/temp.png",
    "name": "Плов",
    "text": "Охапка дров и плов готов!",
    "cooking_time": 20,
    "author": {
        "id": 2,
        "username": "Автор",
        "email": "author@test.com",
        "first_name": "Ав",
        "last_name": "Тор",
    },
}


expected_user_list = {
    "count": 2,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 1,
            "username": "Пользователь",
            "email": user_email,
            "first_name": "Поль",
            "last_name": "Зователь",
            "is_subscribed": False,
        },
        {
            "id": 2,
            "username": "Автор",
            "email": "author@test.com",
            "first_name": "Ав",
            "last_name": "Тор",
            "is_subscribed": False,
        },
    ],
}

expected_user_follow = {
    "id": 2,
    "username": "Автор",
    "email": "author@test.com",
    "first_name": "Ав",
    "last_name": "Тор",
    "is_subscribed": True,
    "recipes": [
        {
            "id": 1,
            "name": "Плов",
            "image": "http://testserver/media/recipes/images/temp.png",
            "cooking_time": 20,
        }
    ],
    "recipes_count": 1,
}

expected_recipe_favorite_data = {
    "id": 1,
    "name": "Плов",
    "image": "/media/recipes/images/temp.png",
    "cooking_time": 20,
}

expected_recipe_id_favorite = {
    "id": 1,
    "ingredients": [
        {
            "id": 2,
            "name": "вроде бы мясо",
            "amount": 30,
            "measurement_unit": "г",
        },
        {
            "id": 3,
            "name": "вроде бы не мясо",
            "amount": 100,
            "measurement_unit": "г",
        },
    ],
    "tags": [{"id": 1, "name": "Обед", "color": "#32CD32", "slug": "lunch"}],
    "is_favorited": True,
    "is_in_shopping_cart": False,
    "image": "http://testserver/media/recipes/images/temp.png",
    "name": "Плов",
    "text": "Охапка дров и плов готов!",
    "cooking_time": 20,
    "author": {
        "id": 2,
        "username": "Автор",
        "email": "author@test.com",
        "first_name": "Ав",
        "last_name": "Тор",
    },
}

expected_recipe_id_cart = {
    "id": 1,
    "ingredients": [
        {
            "id": 2,
            "name": "вроде бы мясо",
            "amount": 30,
            "measurement_unit": "г",
        },
        {
            "id": 3,
            "name": "вроде бы не мясо",
            "amount": 100,
            "measurement_unit": "г",
        },
    ],
    "tags": [{"id": 1, "name": "Обед", "color": "#32CD32", "slug": "lunch"}],
    "is_favorited": False,
    "is_in_shopping_cart": True,
    "image": "http://testserver/media/recipes/images/temp.png",
    "name": "Плов",
    "text": "Охапка дров и плов готов!",
    "cooking_time": 20,
    "author": {
        "id": 2,
        "username": "Автор",
        "email": "author@test.com",
        "first_name": "Ав",
        "last_name": "Тор",
    },
}
