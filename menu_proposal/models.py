from django.db import models
from django.urls import reverse
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
        ("名前（Menu name）"), max_length=128, unique=True)
    menu_value = models.IntegerField(("価格（Price (incl. tax)）"))
    menu_energy = models.FloatField(("カロリー（Energy）"))
    menu_carbohydrate = models.FloatField(("炭水化物（Carbohydrates）"))
    menu_salt_content = models.FloatField(("塩分（Salt）"))
    menu_lipid = models.FloatField(("脂質（Fat）"))
    menu_protein = models.FloatField(("タンパク質（Protein）"))
    menu_red_point = models.FloatField(("赤（Red）"))
    menu_green_point = models.FloatField(("緑（Green）"))
    menu_yellow_point = models.FloatField(("黄（Yellow）"))
    menu_picture = models.ImageField(
        ("画像（Image）"), upload_to=get_file_path, height_field=None, width_field=None, max_length=None, null=True, blank=True)
    menu_genre = models.ManyToManyField(Genres, verbose_name=("ジャンル（Genre）"))
    menu_allergies = models.ManyToManyField(
        Allergies, verbose_name=("アレルギー（Allergic substance）"), null=True, blank=True)

    class Meta:
        verbose_name = ("menu")
        verbose_name_plural = ("menus")

    def __str__(self):
        return self.menu_name
