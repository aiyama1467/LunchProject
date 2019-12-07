from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, PasswordChangeForm
)
from django.contrib.auth import get_user_model

from menu_proposal.models import Allergies, Genres

User = get_user_model()


class UserCreateForm(UserCreationForm):
    """ユーザを作成するときのフォーム"""
    allergy = forms.ModelMultipleChoiceField(label="アレルギー", queryset=Allergies.objects.all(),
                                             widget=forms.CheckboxSelectMultiple, required=False)
    genre = forms.ModelMultipleChoiceField(label="好み", queryset=Genres.objects.all(),
                                           widget=forms.CheckboxSelectMultiple)

    """ユーザー登録用フォーム"""
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'allergy', 'genre')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            self.save_m2m()
        return user


class PasswordModifyForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
