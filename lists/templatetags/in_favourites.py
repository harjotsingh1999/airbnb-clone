from django import template
from lists import models as list_models

register = template.Library()


# takes context means it will automatically be sent the request object
@register.simple_tag(takes_context=True)
def in_favourites(context, room):
    user = context.request.user
    print(user)
    favs_list_item, _ = list_models.List.objects.get_or_create(
        user=user, name="My Favourite Houses"
    )
    print(favs_list_item.rooms.all())  # is how you get many to many fields
    print(favs_list_item.count_rooms())

    # if room is already in the favs list means we dont have to
    # show the add to favs button to user again
    return favs_list_item.rooms.filter(pk=room.pk).exists()
