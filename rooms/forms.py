from django import forms
from django.forms.widgets import Widget
from django_countries.fields import CountryField
from . import models

# it also allows us to change/ customise widgets of the fields
# like CharField uses a Textfield but we can make it use textEdit field

# similarly ModelMultiplehoiceField used a dropdown
# but we make it use a check box list


class SearchForm(forms.Form):
    city = forms.CharField(initial="Anywhere")
    country = CountryField(default="IN").formfield()
    room_type = forms.ModelChoiceField(
        required=False, empty_label="Any kind", queryset=models.RoomType.objects.all()
    )
    price = forms.IntegerField(required=False)
    guests = forms.IntegerField(required=False)
    bedrooms = forms.IntegerField(required=False)
    beds = forms.IntegerField(required=False)
    baths = forms.IntegerField(required=False)

    instant_book = forms.BooleanField(required=False)
    superhost = forms.BooleanField(required=False)

    # queryset is important for it to generate fields
    amenities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    facilities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Facility.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )


class CreatePhotoForm(forms.ModelForm):
    class Meta:
        model = models.Photo

        fields = [
            "caption",
            "file",
        ]

    def save(self, pk, *args, **kwargs):
        photo = super().save(commit=False)
        # print("room pk= ", pk)
        room = models.Room.objects.get(pk=pk)
        photo.room = room
        photo.save()


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = models.Room
        fields = [
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
        ]

    """def save(self, user, *args, **kwargs):

        # the room created from the form willnot have a user
        # which is necessary
        # hence we intercept before saving
        # get the user who made the request
        # and save the room with user= that user
        room = super().save(commit=False)
        room.host = user
        room.save()"""

    def save(self, *args, **kwargs):

        # this is important cus
        # the object will be created but not saved
        # so that we can do it manually after assigning the host
        room = super().save(commit=False)
        return room
