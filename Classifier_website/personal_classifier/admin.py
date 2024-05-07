from django.contrib import admin
from .models import RunClassifierData, EmailDataTable, FeatureData, TopicData
# Register your models here.
admin.site.register(RunClassifierData)
admin.site.register(EmailDataTable)
admin.site.register(FeatureData)
admin.site.register(TopicData)