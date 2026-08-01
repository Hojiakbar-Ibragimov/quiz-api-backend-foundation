# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Users(models.Model):
    real_name = models.TextField()
    username = models.TextField(blank=True, null=True)
    active = models.BooleanField(blank=True, default=True)
    role = models.CharField(max_length=10)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'users'


class UserProfiles(models.Model):
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        primary_key=True,
        blank=True,
        related_name='profile')
    bio = models.CharField(max_length=50, blank=True, null=True)
    # avatar = models.ImageField()
    theme = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=2, blank=True)

    class Meta:
        managed = False
        db_table = 'user_profiles'


class UserStatistics(models.Model):
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        primary_key=True,
        blank=True,
        related_name='statistics'
    )
    record_points = models.IntegerField(default=0)
    overall_points = models.IntegerField(default=0)
    played_count = models.IntegerField(default=0)
    won_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_statistics'
