from django.db import models

class Solution(models.Model):
    hash = models.CharField('Hash', max_length=40)
    value = models.CharField('Value', max_length=20)
    ctime = models.DateTimeField('Date created', blank=True, auto_now_add=True)
