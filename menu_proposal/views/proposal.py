from django import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone
from menu_proposal.forms import ProposalForm
from menu_proposal.models import *
from accounts.models import EatLog
import numpy as np
import operator
import itertools
import plotly.offline as opy
import plotly.graph_objs as go


class MenuProposalView(FormView):
    """
    献立提案入力フォーム
    """
    form_class = ProposalForm
    template_name = 'Proposal/proposal_form.html'
    success_url = reverse_lazy('proposal_result')

    def get_initial(self):
        initial = super().get_initial()
        initial['time'] = 1
        if self.request.user.is_authenticated and self.request.user.is_superuser == False:
            user = self.request.user
            # 好みのジャンルの初期値の設定
            genre = []
            for i in user.genre.all():
                genre.append(i.pk)
            initial['like_genre'] = genre
            # アレルギーの初期値の設定
            allergy = []
            for i in user.allergy.all():
                allergy.append(i.pk)
            initial['allergy'] = allergy

        return initial

    def form_valid(self, form):
        # 一回当たりの予算が300未満の時
        if (form.cleaned_data["budget"] / int(form.cleaned_data["time"])) < 300:
            messages.error(
                self.request, "予算の値が小さすぎます。食事一回当たりの予算を300円以上にしてください")
            return super().form_invalid(form)
        # アレルギーリスト
        allergies = []
        for i in form.cleaned_data["allergy"]:
            allergies.append(i.pk)
        # 好みのジャンルリスト
        like_genre = []
        for i in form.cleaned_data["like_genre"]:
            like_genre.append(i.pk)
        # Menu_Proposalを使いおすすめ献立[menu_list]を求める
        proposal = Menu_Proposal(
            int(form.cleaned_data["time"]), allergies, form.cleaned_data["budget"], like_genre)
        menu_list = proposal.propose()
        # おすすめの献立が日数分提案できなかった時メッセージを表示し、入力フォームに戻る
        if len(menu_list) < int(form.cleaned_data["time"]):
            messages.error(self.request, "おすすめ献立を見つけることができませんでした。条件を変えてください")
            return super().form_invalid(form)
        # menu_listから各要素の合計値を求める
        menu_sum_list = []
        menu_graph_list = []
        for menu in menu_list:
            sum = {"税込価格（Price (incl. tax)）": 0, "カロリー（Energy）": 0.0,  "炭水化物（Carbohydrates）": 0.0, "塩分（Salt）": 0.0, "脂質（Fat）": 0.0,
                   "タンパク質（Protein）": 0.0, "赤（Red）": 0.0,  "緑（Green）": 0.0, "黄（Yellow）": 0.0, }
            for i in menu:
                sum["税込価格（Price (incl. tax)）"] += i.menu_value
                sum["カロリー（Energy）"] += i.menu_energy
                sum["炭水化物（Carbohydrates）"] += i.menu_carbohydrate
                sum["塩分（Salt）"] += i.menu_salt_content
                sum["脂質（Fat）"] += i.menu_lipid
                sum["タンパク質（Protein）"] += i.menu_protein
                sum["赤（Red）"] += i.menu_red_point
                sum["緑（Green）"] += i.menu_green_point
                sum["黄（Yellow）"] += i.menu_yellow_point
            menu_sum_list.append(sum)
            x = [sum["炭水化物（Carbohydrates）"], sum["塩分（Salt）"], sum["脂質（Fat）"], sum["タンパク質（Protein）"],
                 sum["赤（Red）"], sum["緑（Green）"], sum["黄（Yellow）"]]
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
            menu_graph_list.append(div)
        data = [go.Bar(
            x=list(reversed(list(sum.values()))),
            y=list(reversed(list(sum.keys()))),
            orientation='h'
        )]
        layout = go.Layout(title="栄養素",
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='rgba(255,255,255,1)'))
        fig = go.Figure(data=data, layout=layout)
        div = opy.plot(fig, auto_open=False, output_type='div')
        # 日付のリスト
        date = [timezone.datetime.today().date()]
        # 土曜日の時,一日目を月曜日に
        if date[0].strftime('%w') == "6":
            date[0] += timezone.timedelta(days=2)
        # 日曜日の時,一日目を月曜日に
        if date[0].strftime('%w') == "0":
            date[0] += timezone.timedelta(days=1)
        # 一般ユーザーが利用したとき食事履歴を追加
        if self.request.user.is_authenticated and self.request.user.is_superuser == False:
            if not EatLog.objects.filter(user=self.request.user, eat_datetime=date[0]).exists():
                log = EatLog.objects.create(
                    user=self.request.user, eat_datetime=date[0])
                for menu in menu_list[0]:
                    log.menu.add(menu)
                messages.info(self.request, "食事履歴を追加しました")
                log.save()
        for i in range(1, int(form.cleaned_data["time"])):

            if date[i - 1].strftime('%w') == '5':
                aa = date[i - 1] + timezone.timedelta(days=3)
            else:
                aa = date[i - 1] + timezone.timedelta(days=1)
            date.append(aa)
            # 一般ユーザーが利用したとき食事履歴を追加
            if self.request.user.is_authenticated and self.request.user.is_superuser == False:
                if not EatLog.objects.filter(user=self.request.user, eat_datetime=date[i]).exists():
                    continue
                log = EatLog.objects.create(
                    user=self.request.user, eat_datetime=date[i])
                for menu in menu_list[0]:
                    log.menu.add(menu)
                log.save()
        # 栄養素の単位のリスト
        unit = ["円", "kcal", "g", "g", "g", "g", "", "", ""]
        # 提案した献立の総栄養素
        result = {}
        trace = []
        graph_list = []
        name = list(menu_sum_list[0].keys())
        for i, d in enumerate(menu_sum_list):
            graph = []
            for j, k in enumerate(d.keys()):
                result[k] = result.get(k, 0) + d[k]
                graph.append(d[k])
            graph_list.append(graph)
        graph_list = list(zip(*graph_list))
        for i, graph in enumerate(graph_list):
            trace.append(go.Scatter(
                x=date, y=graph, mode='lines+markers', name=name[i]))
        layout = go.Layout(xaxis=dict(type='date'),  # dtick: 'M1'で１ヶ月ごとにラベル表示
                           yaxis=dict(),
                           title="推移",
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='rgba(255,255,255,1)'))
        fig = go.Figure(data=trace, layout=layout)
        div2 = opy.plot(fig,  output_type='div')
        return render(self.request, 'Proposal/proposal_result.html', {"date": date, "form": form, "menu": menu_list, "sum": menu_sum_list, "time": range(int(form.cleaned_data["time"])), "total": result, "unit": unit, "graph_list": menu_graph_list, "div": div, "div2": div2, "time_int": int(form.cleaned_data["time"])})

    def form_invalid(self, form):
        messages.error(self.request, "入力に誤りがあります。もう一度正しく入力してください。")
        return super().form_invalid(form)


class Menu_Proposal:
    def __init__(self, time, allergy, budget, like_genre):
        self.time = int(time)
        self.budget = budget / self.time
        self.like_genre = like_genre
        self.staplefood = [i for i in Menu.objects.filter(
            menu_genre__genre_name__in=['丼（Bowl）', '麺（Noodles）', 'ごはん（Rice）']).filter(~Q(menu_allergies__in=allergy))]
        self.maindish = [i for i in Menu.objects.filter(
            menu_genre__genre_name='主菜（Main dish）').filter(~Q(menu_allergies__in=allergy))]
        self.sidedish = [i for i in Menu.objects.filter(
            menu_genre__genre_name='副菜（Side dish）').filter(~Q(menu_allergies__in=allergy))]
        self.dessert = [i for i in Menu.objects.filter(
            menu_genre__genre_name='デザート（Dessert）').filter(~Q(menu_allergies__in=allergy))]
        self.soup = [i for i in Menu.objects.filter(
            menu_genre__genre_name='汁物（Soup）').filter(~Q(menu_allergies__in=allergy))]
        self.maindish.append(Menu(menu_name="null"))
        self.sidedish.append(Menu(menu_name="null"))
        self.dessert.append(Menu(menu_name="null"))
        self.soup.append(Menu(menu_name="null"))

    # ジャンルの一致している個数を求める
    def get_point(self, menu):
        menu_genres = []
        for i in menu:
            if i.menu_name != "null":
                for j in i.menu_genre.all():
                    menu_genres.append(j.pk)

        point = len(list(set(self.like_genre) & set(menu_genres)))
        return point

    # 栄養のバランスを求める
    def get_value(self, menu):
        vec_tmp = np.array([2, 1, 5])
        vec = np.array([0.0, 0.0, 0.0])
        for i in menu:
            vec += ([i.menu_red_point,
                     i.menu_green_point, i.menu_yellow_point])
            if vec[1] != 0.0:
                vec /= vec[1]
            cmp_value = np.linalg.norm(vec_tmp - vec)
        return cmp_value

    def get_price(self, menu_list):
        l = [s for s in menu_list if s.menu_name != 'null']
        # 値段の合計
        price = 0
        for i in l:
            price += i.menu_value
        return price

    def propose(self):
        menu_list = []
        for staple in self.staplefood:
            if self.budget < self.get_price([staple]):
                continue
            # 主食のジャンルのリスト（ごはんと（麺、丼）の時で処理を変える）
            staple_genre = []
            for i in staple.menu_genre.all():
                staple_genre.append(i.genre_name)
            for main in self.maindish:
                if ("ごはん（Rice）" in staple_genre and main.menu_name is "null") or self.budget < self.get_price([staple, main]):
                    continue
                for side in self.sidedish:
                    if ("ごはん（Rice）" in staple_genre and side.menu_name is "null") or self.budget < self.get_price([staple, main, side]):
                        continue
                    for dessert in self.dessert:
                        if self.budget < self.get_price([staple, main, side, dessert]):
                            continue
                        for soup in self.soup:
                            # 献立のリスト
                            l = [staple, main, side, dessert, soup]
                            # 予算オーバーの場合追加しない
                            if self.budget < self.get_price(l):
                                continue
                            # nullの削除
                            l = [s for s in l if s.menu_name != 'null']
                            # 献立の評価 genreの一致率 > menuの栄養
                            # 上位（提案回数）個リストに保存
                            add_menu = False
                            for menu_value in range(min(self.time, len(menu_list))):
                                point = self.get_point(menu_list[menu_value])
                                tmp_point = self.get_point(l)
                                if point < tmp_point:
                                    menu_list.insert(menu_value, l)
                                    add_menu = True
                                    break
                                elif point == tmp_point:
                                    value = self.get_value(
                                        menu_list[menu_value])
                                    cmp_value = self.get_value(l)
                                    if value > cmp_value:
                                        menu_list.insert(menu_value, l)
                                        add_menu = True
                                        break
                            if add_menu:
                                continue
                            if len(menu_list) < self.time:
                                menu_list.append(l)
        menu_list = menu_list[0: self.time]
        return menu_list
