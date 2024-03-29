from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from notes.models import Note
from users.models import User


class NoteList(ListView):
    """Список заметок пользователя"""
    paginate_by = 5
    model = Note
    template_name = 'notes/notes_list.html'
    context_object_name = 'notes'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        context['username'] = username
        return context

    def get_queryset(self):
        username = self.kwargs.get('username')
        return Note.objects.filter(user__username=username)


class CreateNote(CreateView):
    """Создание заметки"""
    model = Note
    fields = ('text',)
    template_name = 'notes/create_note.html'

    def form_valid(self, form):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        form.instance.author = self.request.user
        form.instance.user = user
        messages.success(self.request, "Заметка создана")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username')
        return context

    def get_success_url(self):
        username = self.kwargs.get('username')
        res = reverse_lazy('users:note_list', kwargs={'username': username})
        return res


class UpdateNote(UpdateView):
    """Изменение заметки"""
    model = Note
    fields = ('text',)
    template_name = 'notes/create_note.html'
    context_object_name = 'note'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username')
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Заметка изменена")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        username = self.kwargs.get('username')
        res = reverse_lazy('users:note_list', kwargs={'username': username})
        return res


class DeleteNote(DeleteView):
    """Удаление заметки"""
    model = Note
    template_name = 'notes/confirm_delete_note.html'
    context_object_name = 'taskcase'

    def get_success_url(self):
        username = self.kwargs.get('username')
        res = reverse_lazy('users:note_list', kwargs={'username': username})
        return res

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username')
        return context
