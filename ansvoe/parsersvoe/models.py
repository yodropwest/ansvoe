from django.db import models


# Create your models here.
class Apartments(models.Model):
    id_crm = models.CharField(max_length=4)
    rooms = models.CharField(max_length=2)
