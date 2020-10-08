from django.db import models
from . import managers

# Create your models here.
# all other models except user will have a timestamp property
# so instead of creating in all we have created a core model
# which all other will extend from
class TimeStampedModel(models.Model):
    """ Time Stamped Model """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # this was added in the second last module
    # to intercept the model manager class
    # to give our custom functionality
    # check usage in reservation:views
    objects = managers.CustomModelManager()

    # We don't model to go to the database
    # hence we make this class abstract as below
    class Meta:
        abstract = True
