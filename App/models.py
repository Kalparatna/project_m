from django.db import models

class LearningModule(models.Model):
    topic = models.CharField(max_length=0)
    title = models.CharField(max_length=0)
    description = models.TextField()

    def __str__(self):
        return self.title


class ChatHistory(models.Model):
    user_id = models.IntegerField()  
    tutor_id = models.CharField(max_length=255)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.tutor_id}: {self.message}"  
    


class app_topics(models.Model):
    topic_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic_name





