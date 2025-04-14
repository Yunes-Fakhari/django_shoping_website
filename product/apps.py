from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'
    verbose_name = ' ماژول محصولات '
    icon = 'fa-solid fa-shop'