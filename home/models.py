from PIL import Image
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Comments(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_on = models.DateField()
    description = models.CharField(max_length=1000)


class Category(models.Model):
    name = models.CharField(max_length=100)
    total_ads = models.IntegerField()
    category_image = models.ImageField()

    def __str__(self):
        return str(self.name) + '('+str(self.total_ads)+')'


class Advertisement(models.Model):
    title = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, default="Brand New")
    description = models.CharField(max_length=1000)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_on = models.DateField()
    negotiable = models.BooleanField(default=True)
    used_for = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100)
    premium_ad = models.BooleanField()
    product_image = models.ImageField()
    price = models.FloatField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.product_image:
            img = Image.open(self.product_image.path)
            if img.height > 350 or img.width > 350:
                output_size = (350, 350)
                img.thumbnail(output_size)
                img.save(self.product_image.path)
        self.category.total_ads += 1

    def __str__(self):
        return self.title
