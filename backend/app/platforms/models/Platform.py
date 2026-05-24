from django.db import models


class Platform(models.Model):
    name = models.CharField(max_length=100)
    content_type = models.CharField(max_length=100)
    connection = models.CharField(max_length=100)
    is_open = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
