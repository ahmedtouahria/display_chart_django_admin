import json
from django.contrib import admin
from django.shortcuts import redirect
from .models import Tier, PollForm, QuestionType, Question, Poll, Answer
from .views import *
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
class AnswerAdmin(admin.ModelAdmin):
    model= Answer
    readonly_fields= ("confirm",)
    # Override changelist_view function for access admin pages
    def changelist_view(self, request, extra_context=None):
        # Aggregate new answer per day
        chart_data = (
            Answer.objects.annotate(date=TruncDay("created_at"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )
        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        # variables for show Answer statistics 

        extra_context = extra_context or {
            "chart_data": as_json,
            }

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context) 

admin.site.register(PollForm, PollFormAdmin)
admin.site.register(Answer,AnswerAdmin)

