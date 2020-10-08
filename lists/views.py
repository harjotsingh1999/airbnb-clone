from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rooms import models as room_models
from users import mixins
from . import models

# Create your views here.


@login_required
def save_room(request, pk):
    room = room_models.Room.objects.get_or_none(pk=pk)
    if room is not None:
        # get_or_create returns a tuple of the obj and whether it was created or not
        list_obj, created = models.List.objects.get_or_create(
            user=request.user,
            name="My Favourite Houses",
        )
        list_obj.rooms.add(room)
        messages.success(request, "Added to favourites")
    return redirect(reverse("rooms:detail", kwargs={"pk": pk}))


@login_required
def remove_room(request, pk):
    room = room_models.Room.objects.get_or_none(pk=pk)
    if room is not None:
        # get_or_create returns a tuple of the obj and whether it was created or not
        list_obj, created = models.List.objects.get_or_create(
            user=request.user,
            name="My Favourite Houses",
        )
        list_obj.rooms.remove(room)
        messages.info(request, "Removed from favourites")
    return redirect(reverse("rooms:detail", kwargs={"pk": pk}))


class AllFavouritesView(mixins.LoginRequiredMixin, TemplateView):
    template_name = "lists/list_detail.html"
