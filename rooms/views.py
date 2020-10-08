from django.shortcuts import render, redirect
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.http import Http404
from django.views.generic.edit import FormView, UpdateView
from django_countries import Countries
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users import mixins as user_mixins
from . import models
from . import forms

# Create your views here.
# this function is no longer required, just kept for reference
def all_rooms(request):

    # if the request obj contains a page query get it else defaults to 1
    page = request.GET.get("page", 1)
    # get reference to all room objects in database
    room_list = models.Room.objects.all()
    # creates a django paginator object for high pagination simplification
    paginator = Paginator(room_list, 10, orphans=5)
    # orphans=5 means if there are 5 items or less in last page
    # it will be sent along in the second last page

    """one page object contains a query set of the required rooms in object_list
    as well as several other details such as count for total objects,
    num_pages for total pages
    per_page for um of items per page"""

    """paginator.get_page does all error handling on its own
    whereas paginator.page enables more customization
    by allowing us to handle errors on our own"""

    # rooms = paginator.get_page(page)
    # print(dir(rooms.paginator))

    # the rooms varialble includes rooms.paginator as well
    # which contains more details

    try:
        rooms = paginator.page(page)
        return render(request, "rooms/home.html", {"page": rooms})
    except EmptyPage:
        return redirect("/")
    except PageNotAnInteger:
        return redirect("/")
    except InvalidPage:
        return redirect("/")


# class based views helps reduce boilerplate code even more
# the code above and below do same thing

# function based views as above in general offer more customizability
class HomeView(ListView):

    """ Homeview Model """

    model = models.Room
    paginate_by = 12
    paginate_orphans = 5
    ordering = "created"

    # like /page=2, /page-3.... we can make like /potato=2, or /potato=3
    # basically name of this query argument
    page_kwarg = "page"

    # in the html of this class we will use for room in rooms
    # instead of the default object_list
    context_object_name = "rooms"

    # to add custom data to the view
    """ def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # sending additional key value pairs to the view i.e. room_list.html
        context["now"] = now
        return context """


# a function based view for room detail
# we will also create a class based view below


# the pk argument passed in rooms.urls will be here
def room_detail(request, pk):

    # if the pk in url is something that is not in the database
    # an exception will occur which has to be caught
    try:
        room = models.Room.objects.get(pk=pk)
        return render(request, "rooms/detail.html", context={"room": room})
    except models.Room.DoesNotExist:
        raise Http404()
    # create a "404.html" file to display that particular page
    # return redirect(reverse("core:home"))
    #  or we can do redirect("/") but above keeps professional

    # print(vars(room))


# in urls it is called as views.RoomDetail.as_view()
# unlike function based views which are just called
# as views.function_name


""" but how does django know that we are passing a primary key in the url
 in Detailview, django by default looks for a pk argument
 you can also tell on your own how 'pk' (<int:pk>) looks in the url
 by calling pk_url_kwarg="potato" if url contains <int:potato> """


# also you don't have to explicitly catch exceptions here
# for a page not found, it will automatically throw a 404 error


class RoomDetail(DetailView):

    """ Room Detail Definition"""

    # this is required otherwise Improperly Configured error is thrown
    model = models.Room

    # if html tmeplate not found it will give this error
    # TemplateDoesNotExist at /rooms/178
    # rooms/room_detail.html
    """ FYI the template name is decided by model name
    here Room and the class it inherits here DetailView
    hence template name should be room_detail.html"""


def search(request):

    # the form will forget data next time it reloads
    # form = forms.SearchForm()

    # now it will remember
    country = request.GET.get("country")
    if country:
        form = forms.SearchForm(request.GET)
        # this is a bounded request, this had to be done otherwise
        # it will show us country field is required
        if form.is_valid():
            print("cleaned form data= ", form.cleaned_data)
            # cleaned data will allow us to return the response to the qureies
            # here, rooms matching the filter requirements
            city = form.cleaned_data.get("city")
            country = form.cleaned_data.get("country")
            room_type = form.cleaned_data.get("room_type")
            price = form.cleaned_data.get("price")
            guests = form.cleaned_data.get("guests")
            bedrooms = form.cleaned_data.get("bedrooms")
            beds = form.cleaned_data.get("beds")
            baths = form.cleaned_data.get("baths")
            instant_book = form.cleaned_data.get("instant_book")
            superhost = form.cleaned_data.get("superhost")
            amenities = form.cleaned_data.get("amenities")
            facilities = form.cleaned_data.get("facilities")

            filter_args = {}

            # if there is a city query, i.e., it is not anywhere
            # then we filter the rooms with city starts with the city entered
            if city != "Anywhere":
                filter_args["city__startswith"] = city

            # there is no condition for country since the defaunt is India
            # hence, we filter rooms by country same as entered country
            filter_args["country"] = country

            # condition where no room type is chosen
            # otherwise we filter rooms which have roomtype pk as the entered roomtype pk
            if room_type is not None:
                filter_args["room_type"] = room_type

            # filtering by price
            # if user has filtered by price return all rooms with price
            # less than or equal to that price (lte)
            if price is not None:
                filter_args["price__lte"] = price

            if guests is not None:
                filter_args["guests__gte"] = guests

            if bedrooms is not None:
                filter_args["bedrooms__gte"] = bedrooms

            if beds is not None:
                filter_args["beds__gte"] = beds

            if baths is not None:
                filter_args["baths__gte"] = baths

            if instant_book is True:
                filter_args["instant_book"] = True

            if superhost is True:
                filter_args["host__superhost"] = True

            # filter by amenities
            # because we have a query set of amenities
            # we need to filter by each of them
            for amenity in amenities:
                filter_args["amenities"] = amenity

            # filter by facilities
            # same as above
            for facility in facilities:
                filter_args["facilities"] = facility

            print("entered filter arguments= ", filter_args)
            querySet = models.Room.objects.filter(**filter_args).order_by("-created")
            print("entire query set=", querySet)

            paginator = Paginator(querySet, 10, orphans=5)
            page = request.GET.get("page", 1)

            rooms = paginator.get_page(page)
            print("current page", type(page), page)
            print("current rooms= ", dir(rooms), rooms)
            print(rooms.object_list)
            print(rooms.end_index)
            print(rooms.has_next)
            print(rooms.has_other_pages)
            print(rooms.has_previous)
            print(vars(rooms.paginator))
            print(rooms.number)

            return render(request, "rooms/search.html", {"form": form, "rooms": rooms})

    else:
        form = forms.SearchForm()
        # unbounded request

    return render(request, "rooms/search.html", {"form": form})


# DJANGO forms API (above) helps us achive everything below
"""def search(request):
    # print(request)
    city = request.GET.get("city", "Anywhere")
    city = str.capitalize(city)
    country = request.GET.get("country", "IN")
    room_type = int(request.GET.get("room_type", 0))
    price = int(request.GET.get("price", 0))
    baths = int(request.GET.get("baths", 0))
    guests = int(request.GET.get("guests", 0))
    bedrooms = int(request.GET.get("bedrooms", 0))
    beds = int(request.GET.get("beds", 0))
    instant = bool(request.GET.get("instant", False))
    superhost = bool(request.GET.get("superhost", False))
    s_amenities = request.GET.getlist("amenities")
    s_facilities = request.GET.getlist("facilities")

    print(s_amenities, s_facilities)

    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()

    form_fields = {
        "countries": Countries,
        "room_types": room_types,
        "amenities": amenities,
        "facilities": facilities,
    }

    request_fields = {
        "city": city,
        "s_country": country,
        "s_room_type": room_type,
        "price": price,
        "baths": baths,
        "guests": guests,
        "bedrooms": bedrooms,
        "beds": beds,
        "s_amenities": s_amenities,
        "s_facilities": s_facilities,
        "instant": instant,
        "superhost": superhost,
    }

    to filter and get results we could do models.Room.objects.filter(clause)
    and filter and filter again and again depending upon te query parameters
    checkout Querysets field lookups for documentation
    https://docs.djangoproject.com/en/3.1/ref/models/querysets/#id4

    # or we could do as below

    filter_args = {}

    # if there is a city query, i.e., it is not anywhere
    # then we filter the rooms with city starts with the city entered
    if city != "Anywhere":
        filter_args["city__startswith"] = city

    # there is no condition for country since the defaunt is India
    # hence, we filter rooms by country same as entered country
    filter_args["country"] = country

    # condition where no room type is chosen
    # otherwise we filter rooms which have roomtype pk as the entered roomtype pk
    # if room_type != 0:
    #     filter_args["room_type__pk"] = room_type

    # filtering by price
    # if user has filtered by price return all rooms with price
    # less than or equal to that price (lte)
    if price != 0:
        filter_args["price__lte"] = price

    if guests != 0:
        filter_args["guests__gte"] = guests

    if bedrooms != 0:
        filter_args["bedrooms__gte"] = bedrooms

    if beds != 0:
        filter_args["beds__gte"] = beds

    if baths != 0:
        filter_args["baths__gte"] = baths

    if instant is True:
        filter_args["instant_book"] = True

    if superhost is True:
        filter_args["host__superhost"] = True

    # filter by amenities
    # because we have an array of amenities
    # we need to filter by each of them
    if len(s_amenities) > 0:
        for s_amenity in s_amenities:
            filter_args["amenities__pk"] = int(s_amenity)

    # filter by facilities
    # same as above
    if len(s_facilities) > 0:
        for s_facility in s_facilities:
            filter_args["facilities__pk"] = int(s_facility)

    print(filter_args)
    rooms = models.Room.objects.filter(**filter_args)

    print(rooms)
    print(models.RoomType.objects.get(pk=room_type))

    return render(
        request,
        "rooms/search.html",
        {**form_fields, **request_fields, "rooms": rooms},
    )"""


class EditRoomView(SuccessMessageMixin, user_mixins.LoggedInOnlyView, UpdateView):
    model = models.Room
    template_name = "rooms/room_edit.html"
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "beds",
        "bedrooms",
        "baths",
        "guests",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )

    # success mixin message
    success_message = "Room updated"

    # if you wish to modify forms, like adding placeholders
    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["name"].widget.attrs = {"placeholder": "Name"}
        form.fields["description"].widget.attrs = {"placeholder": "Description"}
        form.fields["country"].widget.attrs = {"placeholder": "Country"}
        form.fields["city"].widget.attrs = {"placeholder": "City"}
        form.fields["price"].widget.attrs = {"placeholder": "Price"}
        form.fields["address"].widget.attrs = {"placeholder": "Address"}
        form.fields["beds"].widget.attrs = {"placeholder": "Number of Beds"}
        form.fields["bedrooms"].widget.attrs = {"placeholder": "Number of Bedrooms"}
        form.fields["baths"].widget.attrs = {"placeholder": "Number of Baths"}
        form.fields["guests"].widget.attrs = {"placeholder": "Number of Guests"}
        form.fields["check_in"].widget.attrs = {"placeholder": "Check In Time"}
        form.fields["check_out"].widget.attrs = {"placeholder": "Check Out Time"}
        form.fields["instant_book"].widget.attrs = {"placeholder": "Instant Book"}
        form.fields["room_type"].widget.attrs = {"placeholder": "Room Type"}
        form.fields["amenities"].widget.attrs = {"placeholder": "Amenities"}
        form.fields["facilities"].widget.attrs = {"placeholder": "Facilities"}
        form.fields["house_rules"].widget.attrs = {"placeholder": "House Rules"}
        return form

    # this is for protection since we don't want to allow
    # users who is not the owner of the room
    # to edit that room
    # we don't show the button to edit to except the owner
    # however now even if the person tries to manipulate the url
    # we show a 404 error
    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        # print("edit room=", room)
        if room.host.pk is not self.request.user.pk:
            raise Http404()
        return room


class RoomPhotosView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, DetailView):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        # print("edit room=", room)
        if room.host.pk is not self.request.user.pk:
            raise Http404()
        return room


# function based view to delete a photo of the room
@login_required
def delete_photo(request, room_pk, photo_pk):
    # print("should delete ", photo_pk, "from", room_pk)
    print(request)

    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            # if this user does not own the room
            messages.error(request, "Can't delete that photo")
        else:
            # if this user owns the room
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo deleted")
        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect("core:home")


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    model = models.Photo
    template_name = "rooms/photo_edit.html"
    fields = {
        "caption",
    }
    pk_url_kwarg = "photo_pk"

    success_message = "Photo updated"

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, FormView):
    model = models.Photo
    template_name = "rooms/photo_create.html"
    fields = {"file", "caption"}
    form_class = forms.CreatePhotoForm

    success_message = "Photo Added"

    # a photo requires a room
    # so we call this method to intercept the valid form
    # and send the pk of the room for the photo before the photo gets saved
    # this is because the photo has to have a room foreign key
    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))


class CreateRoomVIew(user_mixins.LoggedInOnlyView, FormView):
    form_class = forms.CreateRoomForm
    template_name = "rooms/room_create.html"

    def form_valid(self, form):
        # send the user as the host of the room which is being created
        # form.save(self.request.user)
        # a different way would be is returning the room from the form here
        # and adding host to that room here itself and saving it
        # which is what is done here so that upon successful creation of the room
        # the user can be sent to room detail page

        room = form.save()
        room.host = self.request.user
        room.save()

        # don,t forget to do this if you are interceptiong the form
        # or else the many to many fields will not get saved
        form.save_m2m()
        messages.success(self.request, "Room Created")
        return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))
