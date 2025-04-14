from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'User'
    verbose_name = 'محصولات مورد علاقه'
    icon = 'fa-solid fa-heart' # FontAwesome icon for the app (optional)
    
    priority = 0  # Determines the order of the app in the sidebar (higher values appear first, optional)
