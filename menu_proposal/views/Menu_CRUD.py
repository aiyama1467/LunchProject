from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import *
from django.urls import reverse_lazy
from django.db.models import Q
from menu_proposal.models import *
from django import forms
from menu_proposal.forms import *
from django.core.exceptions import PermissionDenied
import plotly.offline as opy
import plotly.graph_objs as go


class MenuCreateView(CreateView):
    model = Menu
    template_name = "Menu/create.html"
    fields = '__all__'
    success_url = reverse_lazy('menu_proposal:edit')

    def dispatch(self, *args, **kwargs):

        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(self.request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['menu_genre'].widget = forms.CheckboxSelectMultiple()
        form.fields['menu_genre'].queryset = Genres.objects
        form.fields['menu_allergies'].widget = forms.CheckboxSelectMultiple()
        form.fields['menu_allergies'].queryset = Allergies.objects
        return form

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '「{}」を作成しました'.format(form.instance))
        return result


class MenuDetailView(DetailView):
    model = Menu
    template_name = "Menu/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        x = [context["menu"].menu_carbohydrate, context["menu"].menu_salt_content, context["menu"].menu_lipid, context["menu"].menu_protein,
             context["menu"].menu_red_point, context["menu"].menu_green_point, context["menu"].menu_yellow_point]
        y = ["炭水化物", "塩分", "脂質", "タンパク質", "赤", "緑", "黄"]
        data = [go.Bar(
            x=list(reversed(x)),
            y=list(reversed(y)),
            orientation='h'
        )]
        layout = go.Layout(title="栄養素",
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='rgba(255,255,255,1)'))
        fig = go.Figure(data=data, layout=layout)
        div = opy.plot(fig, auto_open=False, output_type='div')
        context["graph"] = div
        return context


class MenuListView(ListView):
    model = Menu
    template_name = "Menu/list.html"
    paginate_by = 10

    def post(self, request, *args, **kwargs):
        form_value = [
            self.request.POST.get('name', None),
            self.request.POST.getlist('genre'),
            self.request.POST.getlist('allergy')
        ]

        if 'order_name' == self.request.POST.get('order'):
            form_value.append('order_name')
            form_value.append(self.request.POST.get('order_by_name'))

        if 'order_price' == self.request.POST.get('order'):
            form_value.append('order_price')
            form_value.append(self.request.POST.get('order_by_price'))

        request.session['form_value'] = form_value
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        name = ''
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            menu = form_value[0]
        default_data = {
            'name': name,  # タイトル
        }
        test_form = MenuSearchForm(initial=default_data)  # 検索フォーム
        context['test_form'] = test_form
        return context

    def get_queryset(self):
        # sessionに値がある場合、その値でクエリ発行する。
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            menu = form_value[0]
            genres = form_value[1]
            allergies = form_value[2]
            order_by = form_value[3]
            order = form_value[4]

            # 検索条件
            condition_menu = Q()
            condition_genre = Q()
            condition_allergies = Q()
            if len(menu) != 0 and menu[0]:
                condition_menu = Q(menu_name__icontains=menu)
            if len(genres) != 0:
                condition_genre = Q(menu_genre__in=genres)
            if len(allergies) != 0:
                condition_allergies = ~Q(menu_allergies__in=allergies)

            if order_by == 'order_name':
                if order == 'ascend':
                    return Menu.objects.select_related().filter(condition_menu & condition_genre & condition_allergies).order_by('menu_name')
                else:
                    return Menu.objects.select_related().filter(condition_menu & condition_genre & condition_allergies).order_by('menu_name').reverse()

            elif order_by == 'order_price':
                if order == 'ascend':
                    return Menu.objects.select_related().filter(condition_menu & condition_genre & condition_allergies).order_by('menu_value')
                else:
                    return Menu.objects.select_related().filter(condition_menu & condition_genre & condition_allergies).order_by('menu_value').reverse()

        else:
            # 何も返さない
            return Menu.objects.none()


class MenuEditView(ListView):
    model = Menu
    template_name = "Menu/superuserlist.html"
    paginate_by = 10

    def dispatch(self, *args, **kwargs):

        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_value = [
            self.request.POST.get('name', None),
            self.request.POST.getlist('genre'),
            self.request.POST.getlist('allergy')
        ]
        request.session['form_value'] = form_value
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        name = ''
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            menu = form_value[0]
        default_data = {'name': name,  # タイトル
                        }
        test_form = MenuSearchForm(initial=default_data)  # 検索フォーム
        context['test_form'] = test_form
        return context

    def get_queryset(self):
        # sessionに値がある場合、その値でクエリ発行する。
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            menu = form_value[0]
            genres = form_value[1]
            allergies = form_value[2]
            # 検索条件
            condition_menu = Q()
            condition_genre = Q()
            condition_allergies = Q()
            if len(menu) != 0 and menu[0]:
                condition_menu = Q(menu_name__icontains=menu)
            if len(genres) != 0:
                condition_genre = Q(menu_genre__in=genres)
            if len(allergies) != 0:
                condition_allergies = ~Q(menu_allergies__in=allergies)
            return Menu.objects.select_related().filter(condition_menu & condition_genre & condition_allergies)
        else:
            # 何も返さない
            return Menu.objects.none()


class MenuUpdateView(UpdateView):
    model = Menu
    template_name = "Menu/update.html"
    fields = '__all__'
    success_url = reverse_lazy('menu_proposal:edit')

    def dispatch(self, *args, **kwargs):

        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(self.request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['menu_genre'].widget = forms.CheckboxSelectMultiple()
        form.fields['menu_genre'].queryset = Genres.objects
        form.fields['menu_allergies'].widget = forms.CheckboxSelectMultiple()
        form.fields['menu_allergies'].queryset = Allergies.objects
        return form

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, '「{}」を更新しました'.format(form.instance))
        return result


class MenuDeleteView(DeleteView):
    model = Menu
    template_name = "Menu/delete.html"
    success_url = reverse_lazy('menu_proposal:edit')

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(self.request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, '「{}」を削除しました'.format(self.object))
        return result
