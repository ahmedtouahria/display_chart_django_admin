import json
from django.contrib import admin
from django.shortcuts import redirect
from .models import Tier, PollForm, QuestionType, Question, Poll, Answer
from .views import *
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay
class QuestionInline(admin.StackedInline):
    model = Question

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
        '''Algorithm Logic for STATISTICS'''
        yes_no=0
        dvc=0
        qcm=0
        qcu=0
        qo=0
        answers=Answer.objects.all()
        for i in answers:
            type=i.question.question_type.designation
            if type == "Demande de Valeur Chifrée":
                dvc=dvc+1
            elif type == "Question à Choix Unique":
                qcu=qcu+1
            elif type == "Question à Choix Multiples":
                qcm=qcm+1
            elif type == "Oui / Non Question":
                yes_no=yes_no+1
            elif type == "Question Ouverte":
                qo=qo+1
        extra_context = extra_context or {
            "chart_data": as_json,
            "yes_no":yes_no,
            "dvc":dvc,
            "qcm":qcm,
            "qcu":qcu,
            "qo":qo,
            }

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context) 
    def save_model(self, request, obj, form, change):
        if obj.confirm==False:
            #for get tier mail
            poll_id = obj.poll.id
            poll = Poll.objects.get(id=poll_id)
            print(poll.tier.email)
            #save Answer object with confirm = False
            super().save_model(request, obj, form, change)
            # call success function for sending mail to tier 
            success(request,obj.id,poll.tier.email)
    # override
    def get_queryset(self, request):
        qs = super(AnswerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(confirm=True)
class PollFormAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
admin.site.register(PollForm, PollFormAdmin)
admin.site.register(Answer,AnswerAdmin)

admin.site.register(Tier)
admin.site.register(QuestionType)
admin.site.register(Poll)
