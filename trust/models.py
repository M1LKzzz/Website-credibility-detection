from django.db import models
from django.utils import timezone
import datetime


class History(models.Model):
    url = models.CharField(max_length=50)
    trust_value = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    have_dangerous_file = models.BooleanField(default=False)