from django.db import models
class Promts(models.Model):
    text = models.TextField()
    sentiment_label = models.CharField(max_length=255, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    emotion_label = models.CharField(max_length=255, blank=True, null=True)
    emotion_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.text
    
class CsvData(models.Model):
    text = models.TextField()
    likes = models.IntegerField()
    comments = models.IntegerField()
    shares = models.IntegerField()
    reactions_count = models.IntegerField()

    def __str__(self):
        return self.text