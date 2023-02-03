from django.contrib import admin

from tasks.models import Answer, Review, Task, TaskCase, UserTaskCaseRelation, UserTaskRelation


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1


class UserTaskRelationAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)


class AnswerAdmin(admin.ModelAdmin):
    inlines = (ReviewInline,)


admin.site.register(TaskCase)
admin.site.register(Task)
admin.site.register(Review)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(UserTaskCaseRelation)
admin.site.register(UserTaskRelation, UserTaskRelationAdmin)
