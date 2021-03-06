from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from menu_proposal.models import Allergies, Genres, Menu


class _UserManager(UserManager):
    """
    ユーザインスタンスを作成するクラス
    """
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """ユーザ"""
    username = models.CharField(_('username'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    allergy = models.ManyToManyField(Allergies, blank=True, null=True)
    genre = models.ManyToManyField(Genres)

    objects = _UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class EatLog(models.Model):
    """食事の履歴"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    eat_datetime = models.DateField()
    menu = models.ManyToManyField(Menu)
