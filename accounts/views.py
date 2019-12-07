from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

from collections import OrderedDict

from accounts.models import User, EatLog
from .forms import UserCreateForm, PasswordModifyForm, ModifyUserInfoForm


class OnlyYouMixin(UserPassesTestMixin):
    """
    異なるユーザからのアクセスを防ぐアクセス制限
    """
    raise_exception = False

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


class UserMyPage(generic.TemplateView):
    """マイページのView"""
    template_name = 'accounts/user_my_page.html'

    class Data:
        __slots__ = ['tax_rate', 'menu', 'price', 'energy', 'carbohydrates', 'salt', 'fat', 'protein', 'red', 'green', 'yellow']

        def __init__(self, menu=None):
            self.tax_rate = 1.1

            if menu is not None:
                self.menu = [menu.menu_name]
                self.price = menu.menu_value * self.tax_rate
                self.energy = menu.menu_energy
                self.carbohydrates = menu.menu_carbohydrate
                self.salt = menu.menu_salt_content
                self.fat = menu.menu_lipid
                self.protein = menu.menu_protein
                self.red = menu.menu_red_point
                self.green = menu.menu_green_point
                self.yellow = menu.menu_yellow_point
            else:
                self.menu = list()
                self.price = self.energy = self.carbohydrates = self.salt = self.fat = self.protein = self.red = self.green = self.yellow = 0

        def __add__(self, other):
            self.menu += other.menu
            self.price += other.price
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

        context['user'] = User.objects.get(id=self.request.user.id)

        eat_log = EatLog.objects.filter(user=self.request.user)
        nutrient_shift = OrderedDict()

        for log in eat_log:
            if log.eat_datetime.isoformat() not in nutrient_shift.keys():
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


class PasswordModifyView(PasswordChangeView):
    form_class = PasswordModifyForm
    success_url = reverse_lazy('accounts:password_modify_done')
    template_name = 'accounts/modify_password.html'


class PasswordModifyDoneView(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'accounts/password_modify_done.html'


class ModifyUserInfoView(LoginRequiredMixin, generic.FormView):
    form_class = ModifyUserInfoForm
    template_name = 'accounts/modify_user_info.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=request.user)

        if form.is_valid():
            form.save()

        return redirect('accounts:my_page')

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user

        initial['email'] = user.email

        # 好みのジャンルの初期値の設定
        genre = []
        for g in user.genre.all():
            genre.append(g.pk)
        initial['genre'] = genre
        # アレルギーの初期値の設定
        allergy = []
        for a in user.allergy.all():
            allergy.append(a.pk)
        initial['allergy'] = allergy

        return initial

# Todo: signup, login, logoutのページのレイアウトを調整する
