from django.urls import path

from tasks.views import AddTaskCaseUsers, AddTaskTaskCase, CreateTask, CreateTaskCase, CreateTest, \
    DeleteTask, \
    DeleteTaskCase, \
    TaskCaseList, \
    TaskCaseListAdmin, \
    TaskDetail, \
    TaskDetailAdmin, TaskListAdmin, \
    TaskListTestAdmin, TaskListUser, \
    TestDetailAdmin, UpdateTask, UpdateTaskCase, UpdateTest, add_answer, add_variant, add_variants_to_user, \
    complete_taskcase, \
    complete_taskcase_admin, delete_variant, \
    update_variant

app_name = 'tasks'

urlpatterns = [
    path('', TaskCaseList.as_view(), name='taskcase_list'),
    path('<int:pk>/task_list', TaskListUser.as_view(), name='task_list'),
    path('<int:pk>/task_detail/<int:id>/', TaskDetail.as_view(), name='task_detail'),
    path('<int:pk>/task_detail/<int:id>/test', add_variants_to_user, name='task_detail_test'),
    path('<int:pk>/task_detail/<int:id>/add_answer', add_answer, name='add_answer'),
    path('<int:pk>/task_detail/<int:id>/add_test_answer', add_variants_to_user, name='add_variant'),
    path('tasks/', TaskListAdmin.as_view(), name='task_list_admin'),
    path('tasks/tests/', TaskListTestAdmin.as_view(), name='task_list_admin_test'),
    path('tasks/<int:pk>/', TaskDetailAdmin.as_view(), name='task_detail_admin'),
    path('tasks/create_task', CreateTask.as_view(), name='create_task'),
    path('tasks/create_test', CreateTest.as_view(), name='create_test'),
    path('tasks/tests/<int:pk>/', TestDetailAdmin.as_view(), name='test_detail_admin'),
    path('tasks/tests/<int:pk>/add_variant', add_variant, name='add_variant'),
    path('tasks/tests/<int:pk>/<int:id_variant>/update_variant', update_variant, name='update_variant'),
    path('tasks/tests/<int:pk>/<int:id_variant>/delete_variant', delete_variant, name='delete_variant'),
    path('tasks/<int:pk>/update_task/', UpdateTask.as_view(), name='update_task'),
    path('tasks/<int:pk>/update_test/', UpdateTest.as_view(), name='update_test'),
    path('tasks/<int:pk>/delete', DeleteTask.as_view(), name='delete_task'),
    path('tasks_case/', TaskCaseListAdmin.as_view(), name='taskcase_list_admin'),
    path('tasks_case/create', CreateTaskCase.as_view(), name='create_taskcase'),
    path('tasks_case/<int:pk>/complete', complete_taskcase, name='complete_taskcase'),
    path('tasks_case/<int:pk>/complete/<slug:username>/test', complete_taskcase_admin, name='complete_taskcase_admin'),
    path('tasks_case/<int:pk>/update', UpdateTaskCase.as_view(), name='update_taskcase'),
    path('tasks_case/<int:pk>/delete', DeleteTaskCase.as_view(), name='delete_taskcase'),
    path('tasks_case/<int:pk>/add_task_taskcase', AddTaskTaskCase.as_view(), name='add_task_taskcase'),
    path('tasks_case/<int:pk>/add_user_taskcase', AddTaskCaseUsers.as_view(), name='add_user_taskcase'),
]
