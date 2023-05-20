from django.db import models


class Top_Games_Categories(models.Model):
    name = models.CharField(max_length=100)
    developer = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    date_released = models.DateField()
    review_category = models.CharField(max_length=100)
    review_score = models.IntegerField()
    metacritic_score = models.IntegerField()
    review_amount = models.IntegerField()
    original_price = models.DecimalField(max_digits=6, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=6, decimal_places=2)
    achievements_listed = models.IntegerField()
    game_rating = models.CharField(max_length=100)
    dlc = models.BooleanField()
    early_access = models.BooleanField()
    category = models.CharField(max_length=50)

