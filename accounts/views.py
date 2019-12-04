from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from accounts.models import User
from .forms import UserCreateForm


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
            return redirect('accounts:signup_successful')

        return render(request, self.template_name, self.context)


class SignupSuccessful(generic.TemplateView):
    template_name = 'accounts/signup_successful.html'

# Todo: signup, login, logoutのページのレイアウトを調整する
