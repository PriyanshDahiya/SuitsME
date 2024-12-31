from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image_url = models.URLField(null=True, blank=True)  # Field to store the URL of the image
    product_url = models.URLField()
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class LikedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.product.name}"

class UserInteraction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    SWIPE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=10, choices=SWIPE_CHOICES)
    interacted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.interaction_type}d {self.product.name}"

class Review(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]  # Show first 50 characters in the admin list

class DailyQuote(models.Model):
    quote = models.TextField()
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.quote
