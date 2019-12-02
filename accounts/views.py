from django.urls import reverse_lazy
from django.views import generic

from .forms import UserCreateForm


class SignUpView(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('accounts:signup_successful')
    template_name = 'accounts/signup.html'


class SignupSuccessful(generic.TemplateView):
    template_name = 'accounts/signup_successful.html'

# Todo: signup, login, logoutのページのレイアウトを調整する
