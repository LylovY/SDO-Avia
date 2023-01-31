from django.urls import include, path

from tasks.views import TaskCaseList, TaskList

app_name = 'tasks'

urlpatterns = [
    path('', TaskCaseList.as_view(), name='taskcase_list'),
    path('<int:pk>/', TaskList.as_view(), name='task_list')
]