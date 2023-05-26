from django.contrib import admin
from .models import User

# Добавление своей модели User в админку.
admin.site.register(User)
