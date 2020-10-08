import datetime
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import View
from django.urls import reverse
from django.contrib import messages
from rooms import models as room_models
from . import models
from reviews import forms as review_forms

# Create your views here.


class CreateError(Exception):
    pass


def create(request, room, year, month, day):
    print(room, year, month, day)
    date_obj = datetime.datetime(year=year, month=month, day=day)
    try:
        room = room_models.Room.objects.get(pk=room)
        # if booking is found on this day in this room
        # we must show an error that room is already taken
        models.BookedDay.objects.get(day=date_obj, reservation__room=room)
        raise CreateError
    except (room_models.Room.DoesNotExist, CreateError):
        # if room does not exist we show an error message
        # this will happen when user messes with the url
        messages.error(request, "Cannot Reserve Room")
        return redirect(reverse("core:home"))
    except models.BookedDay.DoesNotExist:
        # no booked day in this room on this date
        # we must proceed to create reservation
        reservation = models.Reservation.objects.create(
            guest=request.user,
            room=room,
            check_in=date_obj,
            check_out=date_obj + datetime.timedelta(days=1),
        )
        # unfortunately we can create a rservation of one day only

        return redirect(
            reverse(
                "reservations:detail",
                kwargs={
                    "pk": reservation.pk,
                },
            )
        )


class ReservationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = models.Reservation.objects.get_or_none(pk=pk)
        if not reservation:
            raise Http404()
        if (
            reservation.guest != self.request.user
            and reservation.room.host != self.request.user
        ):
            # the user that has requested this page has to either be guest or host
            raise Http404()

        form = review_forms.CreateReviewForm()
        return render(
            self.request,
            "reservations/detail.html",
            {"reservation": reservation, "form": form},
        )


def edit_reservation(request, pk, verb):
    reservation = models.Reservation.objects.get_or_none(pk=pk)
    if not reservation:
        raise Http404()
    if reservation.guest != request.user and reservation.room.host != request.user:
        # the user that has requested this page has to either be guest or host
        raise Http404()

    if verb == "confirm":
        reservation.status = models.Reservation.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = models.Reservation.STATUS_CANCELED
        # delete all booked days for this room
        models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, "Reservation updated")
    return redirect(
        reverse(
            "reservations:detail",
            kwargs={
                "pk": reservation.pk,
            },
        )
    )
