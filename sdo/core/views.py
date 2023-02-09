from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class MyLoginRequiredMixin(LoginRequiredMixin, View):
    """Логин пермишн с переопределенной переадресацией"""
    login_url = '/auth/login/'


class AdminRequiredMixin(MyLoginRequiredMixin):
    """Пермишн для админов"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

