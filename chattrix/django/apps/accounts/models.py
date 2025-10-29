from __future__ import annotations
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class user_avatar(models.Model):

    class Meta:
        abstract = True
    user_avatar = models.ImageField(upload_to='avatars/')

class user_status(models.Model):
    class Meta:
        abstract = True
    STATUS_CHOICES = [
        ("online", "Online"),
        ("offline", "Offline"),
    ]
    user_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="offline")



class User(AbstractUser,user_avatar,user_status):

    id = models.BigIntegerField(primary_key=True, editable=False)
    #将id设置为主键，并不可编辑

    def save(self, *args, **kwargs) -> None:
        """
        Save user and generate 10-digit ID if not set.
        """
        if not self.id:
            # Generate 10-digit user ID
            import random
            while True:
                new_id = random.randint(1000000000, 9999999999)
                if not User.objects.filter(id=new_id).exists():
                    self.id = new_id
                    break
        super().save(*args, **kwargs)