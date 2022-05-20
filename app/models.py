from django.db import models
from django.core.validators import validate_email
from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from .validators import * 
from random import randint



# Create your models here.


class User(models.Model):
    name = models.CharField(validators=[validate_name], max_length=70, default="")
    email = models.EmailField(max_length=70, validators=[validate_email], unique=True, default="")
    contact = models.CharField(validators=[validate_contact], unique=True, max_length=10, default="")
    password = models.CharField(validators=[validate_password], max_length=200, default="")

    def __str__(self):
        return self.name


class SKUItems(models.Model):

    sku_name = models.CharField(max_length=100, unique=True, default="")
    sku_qty = models.IntegerField(default=0)
    sku_rate = models.FloatField(default=0.0)
    sku_serial_no = models.CharField(default="", max_length=200, unique=True)
    sku_barcode_image = models.ImageField(upload_to='barcode/', default='backup/')

    def __str__(self):
        return self.sku_name




'''
class Stock(models.Model):
    stock_name = models.CharField(max_length=100, unique=True, default="")
    stock_qty = models.IntegerField(default=0)
    stock_rate = models.FloatField(default=0)
    is_generated = models.BooleanField(default=False)
    

    def __str__(self):
        return self.stock_name


class StockBarcode(models.Model):
    serial_no = models.CharField(default='', max_length=13, unique=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, default=None, null=True)
    barcode_image = models.ImageField(upload_to="barcode/", default="")

    def __str__(self):
        return self.serial_no
'''
    
