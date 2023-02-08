from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class MyLoginRequiredMixin(LoginRequiredMixin, View):
    login_url = '/auth/login/'

