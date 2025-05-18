from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Items"

   

class StockHistory(models.Model):
    class ActionChoices(models.TextChoices):
        ADD = 'ADD', 'Add'
        REMOVE = 'REMOVE', 'Remove'

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=6, choices=ActionChoices.choices)
    change_amount = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name_plural = "Stock Histories"