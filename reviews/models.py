from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core import models as core_models
from users import models as users_model
from rooms import models as rooms_model

# Create your models here.


class Review(core_models.TimeStampedModel):
    """ Reviews Model Definition """

    review = models.TextField()
    accuracy = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communication = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    cleanliness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    location = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    check_in = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(
        users_model.User, related_name="reviews", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        rooms_model.Room, related_name="reviews", on_delete=models.CASCADE
    )

    # any amount of nesting can be done meaning
    # you can call room from self then host from room and go many layers deep
    def __str__(self):
        return f"{self.review}-{self.room}"

    def rating_average(self):
        avg = (
            self.accuracy
            + self.communication
            + self.cleanliness
            + self.location
            + self.check_in
            + self.value
        ) / 6.0

        return round(avg, 2)

    # column name where rating is diaplayed is changed like this
    rating_average.short_description = "Average Rating"

    class Meta:

        # ordey by reverse of the day the review was created
        # that is newest first
        ordering = ("-created",)
