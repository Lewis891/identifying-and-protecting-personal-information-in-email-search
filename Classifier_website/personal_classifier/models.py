from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class RunClassifierData(models.Model):
    no_of_personal_emails = models.IntegerField(default=0)
    accuracy_percentage = models.FloatField(default=0)

class EmailDataTable(models.Model):
    File = models.TextField(default=" ", primary_key=True)
    To = models.TextField(default=" ")
    From = models.TextField(default=" ")
    Body = models.TextField(default=" ")
    message = models.TextField(default=" ")
    count = models.IntegerField(default=0)
    IsPersonal = models.IntegerField(default=0)
    category = models.TextField(default=" ")
    lemma = models.TextField(default=" ")
    preds_rf = models.TextField(default=" ")
    topic = models.TextField(default = " ")
    percentage = models.FloatField(default = 0)
    ManualClassify = models.TextField(default=" ")
    ManualReason = models.TextField(default=" ")


    def __str__(self):
        return self.File

class FeatureData(models.Model):
    feature_name = models.CharField(max_length=100)
    coefficient = models.FloatField(default=0)

class TopicData(models.Model):
    topic_name = models.TextField(default=" ")
    word = models.TextField(default=" ")
    importance = models.FloatField(default=0)