from django.db import models
from content.models import Outline

class OutlineSection(models.Model):

    outline = models.ForeignKey(Outline, on_delete=models.CASCADE, related_name="sections")

    heading = models.CharField(max_length=500)

    level = models.IntegerField()  # 1 = H1 , 2 = H2 , 3 = H3

    order = models.IntegerField()

    notes = models.TextField(blank=True, null=True)
