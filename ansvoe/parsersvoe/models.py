from django.db import models


# Create your models here.
class Apartments(models.Model):
    id_crm = models.CharField(max_length=4)
    price = models.CharField(max_length=255)
    area = models.CharField(max_length=5, default='null')
    area_living = models.CharField(max_length=5, default='null')
    area_kitchen = models.CharField(max_length=5, default='null')
    floor = models.CharField(max_length=2)
    floor_total = models.CharField(max_length=2)
    building = models.CharField(max_length=50)
    bathroom = models.CharField(max_length=4)
    balcony = models.CharField(max_length=20)
    build_year = models.CharField(max_length=4)
    description = models.CharField(max_length=255)
    property_type = models.CharField(max_length=255)
    rooms = models.CharField(max_length=2)
    house = models.CharField(max_length=4)
    street = models.CharField(max_length=255)


class ApartmentsImage(models.Model):
    id_crm = models.ForeignKey(Apartments, on_delete=models.CASCADE, max_length=10)
    image = models.ImageField(upload_to="uploads/")
