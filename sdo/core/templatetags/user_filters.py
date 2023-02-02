from django import template

from tasks.models import UserTaskRelation

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def addclass_checkbox(field, css):
    return field.as_widget(attrs={'class': css, 'id': 'customSwitch1'})


@register.simple_tag
def user_track_directories(directories, user):
    user_track_directories = directories.filter(owner=user)
    return user_track_directories


@register.simple_tag
def user_task_count(qs):
    tasks = qs.filter(task_relation__status=UserTaskRelation.NEW)
    return tasks.count()