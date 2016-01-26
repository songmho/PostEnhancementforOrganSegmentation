__author__ = 'hanter'

from django.db import models

# Model tutorial is in the Python tutorial #2: https://docs.djangoproject.com/en/1.9/intro/tutorial02/

class TestModel(models.Model):
    char_fld = models.CharField(max_length=200)
    date_fld = models.DateTimeField('date published')
    int_fld = models.IntegerField(default=0)

class TestModel2(models.Model):
    test_model_fld = models.ForeignKey(TestModel, on_delete=models.CASCADE);

