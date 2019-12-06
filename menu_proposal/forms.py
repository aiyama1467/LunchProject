from django import forms
from menu_proposal.models import *
TIME_CHOICE = (
    ('1', '日(一日分)'),
    ('5', '週(五日分)'),
)


class MenuSearchForm(forms.Form):
    name = forms.CharField(
        initial='',
        label='名前',
        required=False
    )


class ProposalForm(forms.Form):
    time = forms.ChoiceField(
        label="食事回数（Number of meals）", choices=TIME_CHOICE, widget=forms.RadioSelect)
    budget = forms.IntegerField(
        label="予算(Budget)", min_value=300, max_value=5000)
    allergy = forms.ModelMultipleChoiceField(label="アレルギー（Allergic substance）",
                                             queryset=Allergies.objects.all(), widget=forms.CheckboxSelectMultiple, required=False, help_text='※複数選択可 ※任意')
    like_genre = forms.ModelMultipleChoiceField(label="好み（Preference）",
                                                queryset=Genres.objects.all(), widget=forms.CheckboxSelectMultiple, help_text="※複数選択可")
