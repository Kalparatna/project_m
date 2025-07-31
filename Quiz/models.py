from django.db import models

class MCQTopic(models.Model):
    title = models.CharField(max_length=255)
    num_questions = models.IntegerField(default=10)

    def __str__(self):
        return self.title

class MCQ(models.Model):
    topic = models.ForeignKey(MCQTopic, related_name='mcqs', on_delete=models.CASCADE)
    question_no = models.IntegerField()
    question = models.CharField(max_length=255)
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.question_no}. {self.question}'
