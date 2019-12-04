from django.views.generic import FormView
from menu_proposal.forms import ProposalForm
from django.urls import reverse_lazy
from menu_proposal.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import *
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django import forms
from django.shortcuts import render
import itertools
from django.core import serializers
import collections
import numpy as np


class MenuProposalView(FormView):
    """
    献立提案入力フォーム
    """
    form_class = ProposalForm
    template_name = 'Proposal/proposal_form.html'
    success_url = reverse_lazy('proposal_result')

    def get_initial(self):
        return super().get_initial()

    def form_valid(self, form):
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
            form.cleaned_data["time"], allergies, form.cleaned_data["budget"], like_genre)
        menu_list = proposal.propose()
        # menu_listから各要素の合計値を求める
        menu_sum_list = []
        for menu in menu_list:
            sum = {"値段": 0, "red": 0.0,  "green": 0.0, "yellow": 0.0,
                   "energy": 0.0, "lipid": 0.0, "salt": 0.0, "carbohydrate": 0.0}
            for i in menu:
                sum["値段"] += i.menu_value
                sum["red"] += i.menu_red_point
                sum["green"] += i.menu_green_point
                sum["yellow"] += i.menu_yellow_point
                sum["energy"] += i.menu_energy
                sum["lipid"] += i.menu_lipid
                sum["salt"] += i.menu_salt_content
                sum["carbohydrate"] += i.menu_carbohydrate
            menu_sum_list.append(sum)

        return render(self.request, 'Proposal/proposal_result.html', {"form": form, "menu": menu_list, "sum": menu_sum_list, "time": range(int(form.cleaned_data["time"]))})

    def form_invalid(self, form):
        return super().form_invalid(form)


class Menu_Proposal:
    def __init__(self, time, allergy, budget, like_genre):
        self.time = int(time)
        self.budget = budget / self.time
        self.like_genre = like_genre
        self.staplefood = [i for i in Menu.objects.filter(
            menu_genre__genre_name__in=['丼', '麺', 'ごはん']).filter(~Q(menu_allergies__in=allergy))]
        self.maindish = [i for i in Menu.objects.filter(
            menu_genre__genre_name='主菜').filter(~Q(menu_allergies__in=allergy))]
        self.sidedish = [i for i in Menu.objects.filter(
            menu_genre__genre_name='副菜').filter(~Q(menu_allergies__in=allergy))]
        self.dessert = [i for i in Menu.objects.filter(
            menu_genre__genre_name='デザート').filter(~Q(menu_allergies__in=allergy))]
        self.soup = [i for i in Menu.objects.filter(
            menu_genre__genre_name='汁物').filter(~Q(menu_allergies__in=allergy))]
        self.maindish.append(Menu(menu_name="null"))
        self.sidedish.append(Menu(menu_name="null"))
        self.dessert.append(Menu(menu_name="null"))
        self.soup.append(Menu(menu_name="null"))

    def get_point(self, menu):
        menu_genres = []
        for i in menu:
            if i.menu_name != "null":
                for j in i.menu_genre.all():
                    menu_genres.append(j.pk)

        point = len(list(set(self.like_genre) & set(menu_genres)))
        return point

    def get_value(self, menu):
        vec_tmp = np.array([2, 1, 5])
        vec = np.array([0.0, 0.0, 0.0])
        for i in menu:
            vec += ([i.menu_red_point,
                     i.menu_green_point, i.menu_yellow_point])
            vec /= vec[1]
            cmp_value = np.linalg.norm(vec_tmp - vec)
        return cmp_value

    def propose(self):
        menu_list = []

        max_value = 100000.0
        max_point = -1000
        for staple in self.staplefood:
            # 主食のジャンルのリスト（ごはんと（麺、丼）の時で処理を変える）
            staple_genre = []
            for i in staple.menu_genre.all():
                staple_genre.append(i.genre_name)
            for main in self.maindish:
                if "ごはん" in staple_genre and main.menu_name is "null":
                    continue
                for side in self.sidedish:
                    if "ごはん" in staple_genre and side.menu_name is "null":
                        continue
                    for dessert in self.dessert:
                        for soup in self.soup:
                            # 献立のリスト
                            l = [staple, main, side, dessert, soup]
                            # nullの削除
                            l = [s for s in l if s.menu_name != 'null']
                            # 値段の合計
                            value = 0
                            for i in l:
                                value += i.menu_value
                            # 予算オーバーの場合
                            if self.budget < value:
                                continue
                            # 献立の評価 genreの一致率 > menuの栄養
                            for menu_value in range(min(5, len(menu_list))):
                                point = self.get_point(menu_list[menu_value])
                                tmp_point = self.get_point(l)
                                if point < tmp_point:
                                    menu_list.insert(menu_value, l)
                                    break
                                elif point == tmp_point:
                                    value = self.get_value(
                                        menu_list[menu_value])
                                    cmp_value = self.get_value(l)
                                    if value > cmp_value:
                                        menu_list.insert(menu_value, l)
                                        break
                            if len(menu_list) < 5:
                                menu_list.append(l)
        menu_list = menu_list[0: self.time]
        return menu_list
