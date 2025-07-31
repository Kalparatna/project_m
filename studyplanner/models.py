from django.db import models

class StudyPlan(models.Model):
    subject = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    difficulty_level = models.CharField(max_length=50)
    goal = models.TextField()
    study_hours = models.IntegerField()
    preferred_time = models.TextField()
    study_plan = models.TextField()

    def __str__(self):
        return f"Study Plan for {self.subject} ({self.difficulty_level})"
