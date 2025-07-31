from django.contrib import admin
from .models import LearningModule,ChatHistory, app_topics

admin.site.register(LearningModule)
admin.site.register(ChatHistory)
admin.site.register(app_topics)