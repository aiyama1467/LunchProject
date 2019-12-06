from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import logout

from collections import OrderedDict

from accounts.models import User, EatLog
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
    """ユーザ登録ページのView"""
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
    """マイページのView"""
    model = User
    template_name = 'accounts/user_my_page.html'
    context_object_name = 'user'

    class Data:
        __slots__ = ['energy', 'carbohydrates', 'salt', 'fat', 'protein', 'red', 'green', 'yellow']

        def __init__(self, menu=None):
            if menu is not None:
                self.energy = menu.menu_energy
                self.carbohydrates = menu.menu_carbohydrate
                self.salt = menu.menu_salt_content
                self.fat = menu.menu_lipid
                self.protein = menu.menu_protein
                self.red = menu.menu_red_point
                self.green = menu.menu_green_point
                self.yellow = menu.menu_yellow_point
            else:
                self.energy = self.carbohydrates = self.salt = self.fat = self.protein = self.red = self.green = self.yellow = 0

        def __add__(self, other):
            self.energy += other.energy
            self.carbohydrates += other.carbohydrates
            self.salt += other.salt
            self.fat += other.fat
            self.protein += other.protein
            self.red += other.red
            self.green += other.green
            self.yellow += other.yellow

            return self

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eat_log = EatLog.objects.filter(user=self.request.user)
        nutrient_shift = OrderedDict()

        for log in eat_log:
            if log.eat_datetime not in nutrient_shift.keys():
                nutrient_shift[log.eat_datetime.isoformat()] = self.Data()

            for m in log.menu.all():
                nutrient_shift[log.eat_datetime.isoformat()] += self.Data(m)

        context['nutrient_shift'] = nutrient_shift

        return context


class UserDeleteView(generic.TemplateView):
    """削除のView"""
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            User.objects.filter(email=self.request.user.email).delete()
            logout(self.request)
            return render(self.request, 'accounts/user_delete.html')
        else:
            return redirect('menu_proposal:home')


# Todo: signup, login, logoutのページのレイアウトを調整する
