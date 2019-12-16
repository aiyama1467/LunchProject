from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

import plotly
import datetime
from collections import OrderedDict

from accounts.models import User, EatLog
from .forms import UserCreateForm, PasswordModifyForm, ModifyUserInfoForm
from menu_proposal.models import Menu
import collections
from django.contrib import messages

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

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/signup_successful.html')

        context = {
            'form': form,
        }

        return render(request, 'accounts/signup.html', context)


class UserMyPage(LoginRequiredMixin, generic.TemplateView):
    """マイページのView"""
    template_name = 'accounts/user_my_page.html'

    class Data:
        __slots__ = ['tax_rate', 'menu', 'price', 'energy', 'carbohydrates', 'salt', 'fat', 'protein', 'red', 'green', 'yellow']

        def __init__(self, menu=None):

            if menu is not None:
                self.menu = [menu.menu_name]
                self.price = menu.menu_value
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

        eat_log = EatLog.objects.filter(user=self.request.user).order_by('eat_datetime')
        nutrient_shift = OrderedDict()
        date_time = list()

        for log in eat_log:
            if log.eat_datetime.isoformat() not in nutrient_shift.keys():
                date_time.append(log.eat_datetime)
                nutrient_shift[log.eat_datetime.isoformat()] = self.Data()

            for m in log.menu.all():
                nutrient_shift[log.eat_datetime.isoformat()] += self.Data(m)

        context['nutrient_shift'] = nutrient_shift

        date = list()
        _3m_ago = datetime.date.today() - datetime.timedelta(days=6)
        for d in range(7):
            date.append(_3m_ago + datetime.timedelta(days=d))

        data = list()
        nut = {
            'price': [],
            'energy': [],
            'carbohydrates': [],
            'salt': [],
            'fat': [],
            'protein': [],
            'red': [],
            'green': [],
            'yellow': []
        }
        for d in date:
            if d.isoformat() in nutrient_shift.keys():
                key = d.isoformat()
                nut['price'].append(nutrient_shift[key].price)
                nut['energy'].append(nutrient_shift[key].energy)
                nut['carbohydrates'].append(nutrient_shift[key].carbohydrates)
                nut['salt'].append(nutrient_shift[key].salt)
                nut['fat'].append(nutrient_shift[key].fat)
                nut['protein'].append(nutrient_shift[key].protein)
                nut['red'].append(nutrient_shift[key].red)
                nut['green'].append(nutrient_shift[key].green)
                nut['yellow'].append(nutrient_shift[key].yellow)

            else:
                nut['price'].append(0)
                nut['energy'].append(0)
                nut['carbohydrates'].append(0)
                nut['salt'].append(0)
                nut['fat'].append(0)
                nut['protein'].append(0)
                nut['red'].append(0)
                nut['green'].append(0)
                nut['yellow'].append(0)

        for g in nut.keys():
            data.append(plotly.graph_objs.Scatter(x=date, y=nut[g], name=g))

        layout = plotly.graph_objs.Layout(
            xaxis={"title": "日付"},
            yaxis={"title": "栄養素", "rangemode":"tozero"},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,1)')
        )
        figure = plotly.graph_objs.Figure(data=data, layout=layout)
        div = plotly.offline.plot(figure, auto_open=False, output_type='div')
        context['graph'] = div

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

        context = {
            'form': form
        }

        return render(request, 'accounts/modify_user_info.html', context)

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


class ModifyEatLogView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'accounts/modify_eatlog.html'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_list'] = Menu.objects.all()
        #現在の献立のリストを受け取る
        if request.POST.getlist('eat_log', None):
            context['eatlog_list'] = self.request.POST.getlist('eat_log', None)

        #追加を押されたとき、そのメニューを追加
        if request.POST.get('add', None):
            add = request.POST.get('add', None)
            if 'eatlog_list' in context.keys():
                context['eatlog_list'].append(add)
            else:
                context['eatlog_list'] = [add]

            eatlog = [int(i) for i in context['eatlog_list']]
            eatlog.sort()
            context['eatlog_list']=eatlog

        #削除を押されたとき、そのメニューを削除
        if request.POST.get('del', None):
            delete = request.POST.get('del', None)
            context['eatlog_list'].remove(delete)

        #決定を押されたとき、食事履歴を更新
        if request.POST.get('update', None):
            if 'eatlog_list' in context.keys():
                eatlog = [int(i) for i in context['eatlog_list']]
            else:
                messages.error(self.request, 'メニューを一つ以上指定してください')
                return render(request, 'accounts/modify_eatlog.html', context)
            log_list = EatLog.objects.filter(
                user=self.request.user, eat_datetime=self.kwargs.get('date'))
            log_list=[i for i in log_list]

            eatlog_tuple = collections.Counter(eatlog)
            eatlog_tuple = eatlog_tuple.most_common()

            for i in range(eatlog_tuple[0][1]):
                dup = [x for x in set(eatlog) if eatlog.count(x) > i]
                if len(log_list) > i:
                    log_list[i].menu.set(dup)
                else:
                    log_list.append(EatLog.objects.create(
                        user=self.request.user, eat_datetime=self.kwargs.get('date')))
                    log_list[i].menu.set

            for log in range(eatlog_tuple[0][1], len(log_list)):
                log_list[log].delete()

            del log_list[eatlog_tuple[0][1]:]

            for log in log_list:
                log.save()
            messages.success(self.request, str(
                self.kwargs.get('date')) + 'の献立を修正しました')
            return redirect('accounts:my_page')

        return render(request, 'accounts/modify_eatlog.html', context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ls = EatLog.objects.filter(
            user=self.request.user, eat_datetime=self.kwargs.get('date'))
        eatlog=[]
        for log in ls:
            for menu in log.menu.all():
                eatlog.append(menu.id)
        eatlog.sort()
        context["eatlog_list"] = eatlog
        context["menu_list"] = Menu.objects.all()
        return context


class AddEatLogView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'accounts/add_eatlog.html'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_list'] = Menu.objects.all()
        if request.POST.get('add_date', None):
            context['date'] = request.POST.get('add_date', None)

        #現在の献立のリストを受け取る
        if request.POST.getlist('eat_log', None):
            context['eatlog_list'] = self.request.POST.getlist('eat_log', None)

        #追加を押されたとき、そのメニューを追加
        if request.POST.get('add', None):
            add = request.POST.get('add', None)
            if 'eatlog_list' in context.keys():
                context['eatlog_list'].append(add)
            else:
                context['eatlog_list'] = [add]

            eatlog = [int(i) for i in context['eatlog_list']]
            eatlog.sort()
            context['eatlog_list'] = eatlog

        #削除を押されたとき、そのメニューを削除
        if request.POST.get('del', None):
            delete = request.POST.get('del', None)
            context['eatlog_list'].remove(delete)

        #決定を押されたとき、食事履歴を追加
        if request.POST.get('update', None):
            if 'eatlog_list' in context.keys():
                eatlog = [int(i) for i in context['eatlog_list']]
            else:
                messages.error(self.request, 'メニューを一つ以上指定してください')
                return render(request, 'accounts/add_eatlog.html', context)

            if request.POST.get('add_date', None):
                context['date'] = request.POST.get('add_date', None)
                date = request.POST.get('add_date', None)
            else:
                messages.error(self.request, '日付を指定してください')
                return render(request, 'accounts/add_eatlog.html', context)

            log_list = []

            eatlog_tuple = collections.Counter(eatlog)
            eatlog_tuple = eatlog_tuple.most_common()

            for i in range(eatlog_tuple[0][1]):
                dup = [x for x in set(eatlog) if eatlog.count(x) > i]
                log_list.append(EatLog.objects.create(
                    user=self.request.user, eat_datetime=date))
                log_list[i].menu.set(dup)
            for log in log_list:
                log.save()
            messages.success(self.request, str(date) + 'の献立を追加しました')
            return redirect('accounts:my_page')

        return render(request, 'accounts/add_eatlog.html', context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["menu_list"] = Menu.objects.all()
        return context


class DeleteEatLogView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'accounts/del_eatlog.html'

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete', None):
            log_list = EatLog.objects.filter(user=self.request.user, eat_datetime=self.kwargs.get('date'))
            for i in log_list:
                i.delete()
            messages.success(self.request, str(
                self.kwargs.get('date')) + 'の献立を削除しました')
            return redirect('accounts:my_page')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs.get('date')
        ls = EatLog.objects.filter(
            user=self.request.user, eat_datetime=self.kwargs.get('date'))
        eatlog = []
        for log in ls:
            for menu in log.menu.all():
                eatlog.append(menu.id)
        eatlog.sort()
        context["eatlog_list"] = eatlog
        return context


# Todo: signup, login, logoutのページのレイアウトを調整する
