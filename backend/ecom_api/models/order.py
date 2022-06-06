from django.db import models
from django.contrib.auth.models import User
from .product import Product

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paymentMethod = models.CharField(max_length=200, default='')
    taxPrice = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    shippingPrice = models.DecimalField(max_digits=7, decimal_places=2, default=10.00)
    totalPrice = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    isDelivered = models.BooleanField(default=False)
    deliveredAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    _id = models.AutoField(primary_key=True, editable=False)
    history = AuditlogHistoryField()

    class Meta:
        ordering: ['-createdAt']


    def __str__(self):
        return str(self.createdAt)



class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    image = models.CharField(max_length=200, null=True, blank=True)
    _id = models.AutoField(primary_key=True, editable=False)

    class Meta:
        order_with_respect_to = 'order'

    def __str__(self):
        return str(self.name)



class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    postalCode = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    _id = models.AutoField(primary_key=True, editable=False)

    class Meta:
        order_with_respect_to = 'order'

    def __str__(self):
        return str(self.address)



auditlog.register(User)
auditlog.register(Order)
auditlog.register(OrderItem)
auditlog.register(ShippingAddress)
