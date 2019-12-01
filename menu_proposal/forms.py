from django import forms

TIME_CHOICE = (
    ('1', '日(一日分)'),
    ('5', '週(五日分)'),
)


class ProposalForm(forms.Form):
    time = forms.ChoiceField(
        label="回数", choices=TIME_CHOICE, widget=forms.RadioSelect)
    budget = forms.IntegerField(label="予算")
    # allergy = forms.ModelMultipleChoiceField(
    #     label="アレルギー", widget=forms.CheckboxSelectMultiple)
    # like_genre = forms.ModelMultipleChoiceField(
    #     label="アレルギー", widget=forms.CheckboxSelectMultiple)
