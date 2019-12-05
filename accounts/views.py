from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import logout

from accounts.models import User
from .forms import UserCreateForm


class OnlyYouMixin(UserPassesTestMixin):
    """
    異なるユーザからのアクセスを防ぐアクセス制限
    """
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class SignUpView(generic.CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('accounts:signup_successful')
    template_name = 'accounts/signup.html'
    context = {
        'user_create_form': form_class()
    }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/signup_successful.html')

        return render(request, self.template_name, self.context)


class UserMyPage(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'accounts/user_my_page.html'
    context_object_name = 'user'


class UserDeleteView(OnlyYouMixin, generic.TemplateView):

    def get(self, request, *args, **kwargs):
        User.objects.filter(email=self.request.user.email).delete()
        logout(self.request)
        return render(self.request, 'accounts/user_delete.html')

# Todo: signup, login, logoutのページのレイアウトを調整する
