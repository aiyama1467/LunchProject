from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
import os


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    name = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images', name)
# Create your models here.


class Allergies(models.Model):

    allergy_name = models.TextField(("アレルギー（Allergic substance）"))

    class Meta:
        verbose_name = ("allergies")
        verbose_name_plural = ("allergies")

    def __str__(self):
        return self.allergy_name


class Genres(models.Model):
    genre_name = models.TextField(("ジャンル名（Genre）"))

    class Meta:
        verbose_name = ("Genres")
        verbose_name_plural = ("Genres")

    def __str__(self):
        return self.genre_name


class Menu(models.Model):

    menu_name = models.CharField(
        ("名前（Menu name）"), max_length=128, help_text="※必須", unique=True)
    menu_value = models.IntegerField(
        ("価格（Price (incl. tax)）"), help_text="※必須・0以上の整数", validators=[MinValueValidator(0)])
    menu_energy = models.FloatField(
        ("カロリー（Energy）"), help_text="※必須・0以上の整数", validators=[MinValueValidator(0.0)])
    menu_carbohydrate = models.FloatField(
        ("炭水化物（Carbohydrates）"), help_text="※必須・0以上の小数", validators=[MinValueValidator(0.0)])
    menu_salt_content = models.FloatField(
        ("塩分（Salt）"), help_text="※必須・0以上の小数", validators=[MinValueValidator(0.0)])
    menu_lipid = models.FloatField(
        ("脂質（Fat）"), help_text="※必須・0以上の小数", validators=[MinValueValidator(0.0)])
    menu_protein = models.FloatField(
        ("タンパク質（Protein）"), help_text="※必須・0以上の小数", validators=[MinValueValidator(0.0)])
    menu_red_point = models.FloatField(
        ("赤（Red）"), help_text="※必須・0以上の小数", validators=[MinValueValidator(0.0)])
    menu_green_point = models.FloatField(
        ("緑（Green）"), help_text="※必須・0以上の小数", validators=[MinValueValidator(0.0)])
    menu_yellow_point = models.FloatField(
        ("黄（Yellow）"), help_text="※必須・0以上の小数", validators=[MinValueValidator(0.0)])
    menu_picture = models.ImageField(
        ("画像（Image）"), help_text="※任意", upload_to=get_file_path, height_field=None, width_field=None, max_length=None, null=True, blank=True)
    menu_genre = models.ManyToManyField(
        Genres, help_text="※1つ以上選択", verbose_name=("ジャンル（Genre）"))
    menu_allergies = models.ManyToManyField(
        Allergies, verbose_name=("アレルギー（Allergic substance）"), help_text="※任意", null=True, blank=True)

    class Meta:
        verbose_name = ("menu")
        verbose_name_plural = ("menus")

    def __str__(self):
        return self.menu_name
