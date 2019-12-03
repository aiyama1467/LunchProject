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


class MenuProposalView(FormView):
    """
    献立提案入力フォーム
    """
    form_class = ProposalForm
    template_name = 'Proposal/proposal_form.html'
    success_url = reverse_lazy('proposal_result')

    def form_valid(self, form):
        # アレルギーリスト
        allergies = []
        for i in form.cleaned_data["allergy"]:
            allergies.append(i.pk)
        # Menu_Proposalを使いおすすめ献立[menu_list]を求める
        proposal = Menu_Proposal(1, allergies)
        menu_list = proposal.propose()

        menu = [i.name for i in Menu._meta.get_fields()]
        sum = {"name": Menu.objects.aggregate(Sum('menu_name')), "red": 0.0, "yellow": 0.0, "green": 0.0,
               "energy": 0.0, "lipid": 0.0, "salt": 0.0, "carbohydrate": 0.0}
        sum["sum"] = []
        for i in menu_list[0]:
            sum["red"] += i.menu_red_point
            sum["green"] += i.menu_green_point
            sum["yellow"] += i.menu_yellow_point
            sum["energy"] += i.menu_energy

        for i in menu:
            sum["sum"].append(Menu.objects.aggregate(Sum(i)))
        # for i in menu:
        #     sum["name"].append(i.menu_name)
        #     sum["red"] += i.menu_red_point
        return render(self.request, 'Proposal/proposal_result.html', {"form": form, "menu": menu_list, "sum": sum})

    def form_invalid(self, form):
        return super().form_invalid(form)


class Menu_Proposal:
    def __init__(self, time, allergy):
        self.time = time
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

    def propose(self):
        menu_list = []
        print(self.staplefood)
        print(self.maindish)
        print(self.sidedish)
        print(self.dessert)
        print(self.soup)
        for staple in self.staplefood:
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
                            l = [staple, main, side,
                                 dessert, soup]
                            menu_list.append(
                                [s for s in l if s.menu_name != 'null'])
        print(len(menu_list))
        return menu_list

        # loopで得た献立をリストに入れる
