from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from notes.views import CreateNote, DeleteNote, NoteList, UpdateNote
from tasks.views import AnswerDetail, TaskCaseListAdminTest, TaskListAdminCheck, TaskListAdminCheckTest, UsersList, \
    accept_answer, add_review
from users.views import AddTaskUser, CreateUser, DeleteUser, TaskCaseUser, UpdateUser

app_name = 'users'
urlpatterns = [
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'
         ),
    path('login/',
         LoginView.as_view(template_name='users/login.html', success_url=reverse_lazy('tasks:taskcase_list')),
         name='login'
         ),
    path('', UsersList.as_view(), name='users_list'),
    path('create/', CreateUser.as_view(), name='create_user'),
    path('<slug:username>/edit/', UpdateUser.as_view(), name='update_user'),
    path('<slug:username>/delete/', DeleteUser.as_view(), name='delete_user'),
    path('<slug:username>/add_taskcase/', TaskCaseUser.as_view(), name='add_taskcase_user'),
    path('<slug:username>/add_task/', AddTaskUser.as_view(), name='add_task_user'),
    path('<slug:username>/notes/', NoteList.as_view(), name='note_list'),
    path('<slug:username>/notes/create_note/', CreateNote.as_view(), name='create_note'),
    path('<slug:username>/notes/<int:pk>/update_note/', UpdateNote.as_view(), name='update_note'),
    path('<slug:username>/notes/<int:pk>/delete_note/', DeleteNote.as_view(), name='delete_note'),
    path('<slug:username>/task/check/', TaskListAdminCheck.as_view(), name='check_task'),
    path('<slug:username>/taskcases/test/check/', TaskCaseListAdminTest.as_view(), name='taskcase_list_admin_test'),
    path('<slug:username>/taskcase/<int:pk>/test/check/', TaskListAdminCheckTest.as_view(), name='check_task_test'),
    path('<slug:username>/check/task/<int:pk>/accept_answer/', accept_answer, name='accept_answer'),
    path('<slug:username>/check/task/<int:pk>/answer/<int:id>/', AnswerDetail.as_view(), name='answer_detail'),
    path('<slug:username>/check/<int:pk>/<int:id>/add_review/', add_review, name='add_review'),
]
