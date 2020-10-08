from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from django.urls import reverse
from core import models as core_model
from users import models as users_model
from cal import Calender


# Create your models here.


class AbstractItem(core_model.TimeStampedModel):
    """ Abstract Item """

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):
    """ Room type definition """

    class Meta:
        verbose_name_plural = "Room Types"


class Amenity(AbstractItem):
    """ Amenity type definition"""

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):
    """ Facility type definition"""

    class Meta:
        verbose_name_plural = "Facilities"


class HouseRule(AbstractItem):
    """ HouseRule Type definition """

    class Meta:
        verbose_name_plural = "House Rules"


class Room(core_model.TimeStampedModel):
    """ Room Model Definition """

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    guests = models.IntegerField(help_text="How many people will be staying?")
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    room_type = models.ForeignKey(
        RoomType, blank=True, related_name="rooms", on_delete=models.SET_NULL, null=True
    )
    amenities = models.ManyToManyField(Amenity, related_name="rooms", blank=True)
    facilities = models.ManyToManyField(Facility, related_name="rooms", blank=True)
    house_rules = models.ManyToManyField(HouseRule, related_name="rooms", blank=True)

    # Connecting room to a host user
    # cascade means if user deleted, delete their rooms as well

    # related name makes "room-set" in users to be just"rooms"
    host = models.ForeignKey(
        users_model.User, related_name="rooms", on_delete=models.CASCADE
    )

    # usually python will show the name of a room object as RoomObject1
    # we can override __str__ method to say what we want the name of
    # any toom object to be

    def __str__(self):
        return self.name

    # this is called when anyone saves a model
    # can be used to intercept and make default changes such as making
    #  a name start with capital, etc. or possibly overriding anything u wish
    # such as self.city="banana" will always save city as banana
    # irrespective of what goes in the city field in the form
    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)

    def total_rating(self):
        all_reviews = self.reviews.all()
        all_ratings = 0
        for review in all_reviews:
            all_ratings += review.rating_average()
        try:
            return round(all_ratings / len(all_reviews), 2)
        except ZeroDivisionError:
            return 0.00

    # adds a "view on site" option to the admin panel
    # that takes us to the same page on actual site
    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def first_photo(self):
        try:
            (photo,) = self.photos.all()[:1]
            # print(photo.file.url)
            return photo.file.url
        except ValueError:
            return None

    def get_next_photos(self):
        photos = self.photos.all()[1:5]
        # print("next photos= ", photos)
        return photos

    # this is for the data in the website
    def get_beds(self):
        if self.beds == 1:
            return "1 bed"
        else:
            return f"{self.beds} beds"

    def get_bedrooms(self):
        if self.bedrooms == 1:
            return "1 bedrooms"
        else:
            return f"{self.beds} bdrooms"

    def get_baths(self):
        if self.baths == 1:
            return "1 baths"
        else:
            return f"{self.baths} baths"

    def get_guests(self):
        if self.guests == 1:
            return "1 guest"
        else:
            return f"{self.guests} guests"

    def get_calenders(self):
        now = timezone.now()
        this_year = now.year
        this_month = now.month
        next_month = this_month + 1
        this_month_cal = Calender(this_year, this_month)
        if this_month == 12:
            next_month = 1
            next_month_cal = Calender(this_year + 1, next_month)
        else:
            next_month_cal = Calender(this_year, next_month)
        return [this_month_cal, next_month_cal]


class Photo(core_model.TimeStampedModel):
    """ Photo Model Definition """

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos")
    room = models.ForeignKey(Room, related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.room.name} - {self.caption}"
