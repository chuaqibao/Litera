from django.db import models

# Create your models here.
class Prompt(models.Model):
    id = models.CharField(max_length=5, unique=True, primary_key=True)
    area = models.CharField(max_length=100)
    prompt = models.TextField()

class Resource(models.Model):
    learner_type = models.CharField(max_length=100)
    content_type = models.CharField(max_length=100)
    link = models.CharField(max_length=1000)
    beginner = models.BooleanField()
    intermediate = models.BooleanField()
    advanced = models.BooleanField()
    