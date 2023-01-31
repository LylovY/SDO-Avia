from django.urls import include, path

from tasks.views import TaskCaseList, TaskCaseListAdmin, TaskDetail, TaskListAdmin, TaskListUser, UsersList, add_answer
from users.views import CreateUser, DeleteUser, UpdateUser

app_name = 'tasks'

urlpatterns = [
    path('', TaskCaseList.as_view(), name='taskcase_list'),
    path('<int:pk>/task_list', TaskListUser.as_view(), name='task_list'),
    path('<int:pk>/task_detail/<int:id>/', TaskDetail.as_view(), name='task_detail'),
    path('<int:pk>/task_detail/<int:id>/add_answer', add_answer, name='add_answer'),
    path('users/', UsersList.as_view(), name='users_list'),
    path('users/create', CreateUser.as_view(), name='create_user'),
    path('users/<slug:username>/edit', UpdateUser.as_view(), name='update_user'),
    path('users/<slug:username>/delete', DeleteUser.as_view(), name='delete_user'),
    path('tasks/', TaskListAdmin.as_view(), name='task_list_admin'),
    path('tasks_case/', TaskCaseListAdmin.as_view(), name='taskcase_list_admin'),
]
