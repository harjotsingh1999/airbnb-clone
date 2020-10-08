import datetime
from django import template
from reservations import models as reservation_models

register = template.Library()


@register.simple_tag()
def is_booked(room, day):
    # print(room, day)

    # the parameter day is what we are getting from the cal.py class
    # it has day, year and month in it
    # so we have to create a datetime object cuz the booked day has date time object
    # and we filter those bookedDay that has the same datetime and the room as the parameters
    if day.number == 0:
        return
    try:
        day = datetime.datetime(year=day.year, month=day.month, day=day.number)
        reservation_models.BookedDay.objects.get(day=day, reservation__room=room)
        return True
    except reservation_models.BookedDay.DoesNotExist:
        return False


# reservation__room is how you filter by foreign keys double underscore
