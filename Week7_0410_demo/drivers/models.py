from django.db import models


class Driver(models.Model):
    driver_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    points = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, default='')
    is_signed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.team})"

    class Meta:
        ordering = ['-points']
