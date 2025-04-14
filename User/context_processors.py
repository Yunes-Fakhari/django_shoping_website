from .models import FavoriteList, FavoriteItem

def favorite_details(request):
    if request.user.is_authenticated:
        try:
            favorite_list = FavoriteList.objects.get(user=request.user)
            favorite_items = FavoriteItem.objects.filter(favorite_list=favorite_list)
            favorite_items_count = favorite_items.count()
        except FavoriteList.DoesNotExist:
            favorite_items = []
            favorite_items_count = 0
    else:
        favorite_items = []
        favorite_items_count = 0

    return {
        'favorite_items': favorite_items,
        'favorite_items_count': favorite_items_count,
    }
