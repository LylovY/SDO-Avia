from django.contrib import admin

from tasks.models import Answer, Task, TaskCase, UserTaskCaseRelation, UserTaskRelation


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


class UserTaskRelationAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)


admin.site.register(TaskCase)
admin.site.register(Task)
admin.site.register(Answer)
admin.site.register(UserTaskCaseRelation)
admin.site.register(UserTaskRelation, UserTaskRelationAdmin)
