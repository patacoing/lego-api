from django.db import models

from theme.models import Theme


class Set(models.Model):
    num = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    num_parts = models.PositiveIntegerField()
    img_url = models.URLField()
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
