from django.contrib import admin

from tasks.models import Task, TaskCase, UserTaskCaseRelation, UserTaskRelation

admin.site.register(TaskCase)
admin.site.register(Task)
# admin.site.register(Answer)
admin.site.register(UserTaskCaseRelation)
admin.site.register(UserTaskRelation)
