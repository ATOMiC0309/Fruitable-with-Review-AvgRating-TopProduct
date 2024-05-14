from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Kategoriya", unique=True)
    image = models.ImageField(upload_to='category/', null=True, blank=True)
    slug = models.SlugField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='subcategories')

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nomi")
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.FloatField()
    is_sale = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    quantity = models.IntegerField(default=0)
    slug = models.SlugField(blank=True, null=True)

    def average_rating(self) -> float:
        return Rating.objects.filter(post=self).aggregate(Avg("rating"))["rating__avg"] or 0

    def __str__(self):
        return self.name

    @property
    def full_price(self):
        if self.is_sale > 0:
            price = self.price - (self.price * self.is_sale / 100)
        else:
            price = self.price
        return round(price, 2)

    @property
    def avg_rating(self):
        ratings = self.rating_set.all()
        if ratings:
            count = 0
            for rating in ratings:
                count += rating.rating
            return count / len(ratings)
        return 0

    @avg_rating.setter
    def avg_rating(self, value):
        # Bu metodni kerakmasa ham qoldiring
        pass


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.post.header}: {self.rating}"


class Email(models.Model):
    email = models.EmailField(null=True, blank=True)


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=150, null=True)
    email = models.EmailField(null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
