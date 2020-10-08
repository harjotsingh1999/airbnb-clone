from datetime import timedelta
from django.db import models
from django.utils import timezone
from core import models as core_models

# Create your models here.

# for every reservation we need to block the days in between the checkin
# and checkout days for this room
class BookedDay(core_models.TimeStampedModel):

    day = models.DateField()
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"

    def __str__(self):
        return f"{self.day} - {self.reservation}"


class Reservation(core_models.TimeStampedModel):

    """ Reservation model definition """

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )

    status = models.CharField(
        choices=STATUS_CHOICES, max_length=12, default=STATUS_PENDING
    )

    # the below "user.User" directly makes use of User model
    # instead of importing that class and writing
    # users_models.User
    guest = models.ForeignKey(
        "users.User", related_name="reservations", on_delete=models.CASCADE
    )

    room = models.ForeignKey(
        "rooms.Room", related_name="reservations", on_delete=models.CASCADE
    )

    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f"{self.room} - {self.check_in}"

    def in_progress(self):
        now = timezone.now().date()

        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True

    def is_finished(self):
        is_finished = timezone.now().date() > self.check_out
        # print(is_finished)
        if is_finished:
            BookedDay.objects.filter(reservation=self).delete()
        return is_finished

    is_finished.boolean = True

    # intercepting the save method
    # because for every reservation that we try to save from now on
    # we must create the booked class as well
    def save(self, *args, **kwargs):
        if self.pk is None:
            # new reservation is being created
            start = self.check_in
            # print(start)
            end = self.check_out
            # print(end)
            difference = end - start
            # print("difference in days= ", difference)

            # find a booked date that has a day between the checkIn and checkout dates
            existing_book_day = BookedDay.objects.filter(
                day__range=(start, end)
            ).exists()

            """what we are basically doing is
            if there is not any booked day in between the dates of checkin and checkout
            means that the room is available for booking
            so as we create a reservation
            we simultaneously create booking objects for all dates between'
            checkin and checkout for that particular room
            meaning for the next user who tries to make a reservation in the same
            checkin and checkout range
            he wont be able to since the dates are blocked"""
            if not existing_book_day:
                # print("not existing")
                super().save(*args, **kwargs)
                # print(difference.days + 1)
                for i in range(difference.days + 1):
                    day = start + timedelta(days=i)
                    # print(day)
                    BookedDay.objects.create(day=day, reservation=self)
                return
        return super().save(*args, **kwargs)
        # else:
        #     # reservation exists already from the seed data when bookings were not made
        #     # so we are not changing the bookings there
        #     return super().save(*args, **kwargs)
