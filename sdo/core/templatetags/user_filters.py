from django import template
from django.shortcuts import get_object_or_404

from tasks.models import UserTaskCaseRelation, UserTaskRelation
from users.models import User

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def addclass_checkbox(field, css):
    return field.as_widget(attrs={'class': css, 'id': 'customSwitch1'})


@register.simple_tag
def task_on_check_count(status):
    task_on_check_count = UserTaskRelation.objects.filter(status=status).count()
    return task_on_check_count


@register.simple_tag
def test_on_check_count():
    # UserTaskRelation.objects.filter(task__is_test=True, status='NEW').exists()
    test_on_check_count = UserTaskCaseRelation.objects.filter(review=True).count()
    return test_on_check_count


@register.simple_tag
def user_task_relation(task, user):
    relation = get_object_or_404(UserTaskRelation, user__username=user, task=task)
    return relation


@register.simple_tag
def user_task_variant(user, task):
    user = get_object_or_404(User, username=user)
    return user.variants.filter(task=task)
