from django.urls import include, path

from tasks.views import CreateTask, CreateTaskCase, DeleteTask, DeleteTaskCase, TaskCaseList, TaskCaseListAdmin, \
    TaskDetail, \
    TaskListAdmin, \
    TaskListUser, \
    UpdateTask, UpdateTaskCase, UsersList, \
    add_answer
from users.views import CreateUser, DeleteUser, TaskCaseUser, TaskUser, UpdateUser

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
    path('users/<slug:username>/add_taskcase', TaskCaseUser.as_view(), name='add_taskcase_user'),
    path('users/<slug:username>/add_task', TaskUser.as_view(), name='add_task_user'),
    path('tasks/', TaskListAdmin.as_view(), name='task_list_admin'),
    path('tasks/create', CreateTask.as_view(), name='create_task'),
    path('tasks/<int:pk>/update', UpdateTask.as_view(), name='update_task'),
    path('tasks/<int:pk>/delete', DeleteTask.as_view(), name='delete_task'),
    path('tasks_case/', TaskCaseListAdmin.as_view(), name='taskcase_list_admin'),
    path('tasks_case/create', CreateTaskCase.as_view(), name='create_taskcase'),
    path('tasks_case/<int:pk>/update', UpdateTaskCase.as_view(), name='update_taskcase'),
    path('tasks_case/<int:pk>/delete', DeleteTaskCase.as_view(), name='delete_taskcase'),
]
