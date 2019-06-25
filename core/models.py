from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from datetime import date

# Create your models here.
CATEGORY_CHOICE = (
    ('S','Shirt'),
    ('SW','Sport wear'),
    ('OW', 'Out wear')
)

LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.ImageField(null=True)
    discount_price = models.FloatField()
    category = models.CharField(choices=CATEGORY_CHOICE, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug':self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={
            'slug':self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("core:remove_from_cart", kwargs={
            'slug':self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(default=date.today)
    def __str__(self):
        return self.user.username


