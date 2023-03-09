from django.urls import path

from notes.views import CreateNote, DeleteNote, NoteList, UpdateNote
from tasks.views import AddTaskCaseUsers, AddTaskTaskCase, AnswerDetail, CreateTask, CreateTaskCase, CreateTest, \
    DeleteTask, \
    DeleteTaskCase, \
    TaskCaseList, \
    TaskCaseListAdmin, \
    TaskCaseListAdminTest, TaskDetail, \
    TaskDetailAdmin, TaskListAdmin, \
    TaskListAdminCheck, TaskListAdminCheckTest, TaskListTestAdmin, TaskListUser, \
    TestDetailAdmin, UpdateTask, UpdateTaskCase, UsersList, \
    accept_answer, add_answer, add_review, add_variant, add_variants_to_user, complete_taskcase, delete_variant, \
    update_variant
from users.views import CreateUser, DeleteUser, TaskCaseUser, AddTaskUser, UpdateUser

app_name = 'tasks'

urlpatterns = [
    path('', TaskCaseList.as_view(), name='taskcase_list'),
    path('<int:pk>/task_list', TaskListUser.as_view(), name='task_list'),
    path('<int:pk>/task_detail/<int:id>/', TaskDetail.as_view(), name='task_detail'),
    path('<int:pk>/task_detail/<int:id>/test', add_variants_to_user, name='task_detail_test'),
    path('<int:pk>/task_detail/<int:id>/add_answer', add_answer, name='add_answer'),
    path('<int:pk>/task_detail/<int:id>/add_test_answer', add_variants_to_user, name='add_variant'),
    path('users/', UsersList.as_view(), name='users_list'),
    path('users/create', CreateUser.as_view(), name='create_user'),
    path('users/<slug:username>/edit', UpdateUser.as_view(), name='update_user'),
    path('users/<slug:username>/delete', DeleteUser.as_view(), name='delete_user'),
    path('users/<slug:username>/add_taskcase', TaskCaseUser.as_view(), name='add_taskcase_user'),
    path('users/<slug:username>/add_task', AddTaskUser.as_view(), name='add_task_user'),
    path('users/<slug:username>/notes', NoteList.as_view(), name='note_list'),
    path('users/<slug:username>/notes/create_note', CreateNote.as_view(), name='create_note'),
    path('users/<slug:username>/notes/<int:pk>/update_note', UpdateNote.as_view(), name='update_note'),
    path('users/<slug:username>/notes/<int:pk>/delete_note', DeleteNote.as_view(), name='delete_note'),
    path('users/<slug:username>/check', TaskListAdminCheck.as_view(), name='check_task'),
    path('users/<slug:username>/check/<int:pk>/test', TaskListAdminCheckTest.as_view(), name='check_task_test'),
    path('users/<slug:username>/check/<int:pk>/accept_answer', accept_answer, name='accept_answer'),
    path('users/<slug:username>/check/<int:pk>/<int:id>', AnswerDetail.as_view(), name='answer_detail'),
    path('users/<slug:username>/check/<int:pk>/<int:id>/add_review', add_review, name='add_review'),
    path('tasks/', TaskListAdmin.as_view(), name='task_list_admin'),
    path('tasks/tests/', TaskListTestAdmin.as_view(), name='task_list_admin_test'),
    path('tasks/<int:pk>/', TaskDetailAdmin.as_view(), name='task_detail_admin'),
    path('tasks/create_task', CreateTask.as_view(), name='create_task'),
    path('tasks/create_test', CreateTest.as_view(), name='create_test'),
    path('tasks/tests/<int:pk>/', TestDetailAdmin.as_view(), name='test_detail_admin'),
    path('tasks/tests/<int:pk>/add_variant', add_variant, name='add_variant'),
    path('tasks/tests/<int:pk>/<int:id_variant>/update_variant', update_variant, name='update_variant'),
    path('tasks/tests/<int:pk>/<int:id_variant>/delete_variant', delete_variant, name='delete_variant'),
    path('tasks/<int:pk>/update/', UpdateTask.as_view(), name='update_task'),
    path('tasks/<int:pk>/delete', DeleteTask.as_view(), name='delete_task'),
    path('tasks_case/', TaskCaseListAdmin.as_view(), name='taskcase_list_admin'),
    path('tasks_case/<slug:username>/test', TaskCaseListAdminTest.as_view(), name='taskcase_list_admin_test'),
    path('tasks_case/create', CreateTaskCase.as_view(), name='create_taskcase'),
    path('tasks_case/<int:pk>/complete', complete_taskcase, name='complete_taskcase'),
    path('tasks_case/<int:pk>/update', UpdateTaskCase.as_view(), name='update_taskcase'),
    path('tasks_case/<int:pk>/delete', DeleteTaskCase.as_view(), name='delete_taskcase'),
    path('tasks_case/<int:pk>/add_task_taskcase', AddTaskTaskCase.as_view(), name='add_task_taskcase'),
    path('tasks_case/<int:pk>/add_user_taskcase', AddTaskCaseUsers.as_view(), name='add_user_taskcase'),
]
