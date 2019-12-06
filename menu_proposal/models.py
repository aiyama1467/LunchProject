from django.db import models
from django.urls import reverse
import uuid
import os


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    name = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images', name)
# Create your models here.

def get_or_create_default_genre():
    default_genre1, _ = Genres.objects.get_or_create(genre_name='和食')
    default_genre2, _ = Genres.objects.get_or_create(genre_name='洋食')
    default_genre3, _ = Genres.objects.get_or_create(genre_name='肉')
    default_genre4, _ = Genres.objects.get_or_create(genre_name='魚')
    default_genre5, _ = Genres.objects.get_or_create(genre_name='野菜')
    default_genre6, _ = Genres.objects.get_or_create(genre_name='フルーツ')
    default_genre7, _ = Genres.objects.get_or_create(genre_name='デザート')
    default_genre8, _ = Genres.objects.get_or_create(genre_name='麺')
    default_genre9, _ = Genres.objects.get_or_create(genre_name='丼')
    default_genre10, _ = Genres.objects.get_or_create(genre_name='主菜')
    default_genre11, _ = Genres.objects.get_or_create(genre_name='ごはん')
    default_genre12, _ = Genres.objects.get_or_create(genre_name='汁物')
   
    return default_genre1, default_genre2, default_genre3, default_genre4, default_genre5, default_genre6, default_genre7, default_genre8, default_genre9, default_genre10, default_genre11, default_genre12

class Allergies(models.Model):
    allergy_name = models.TextField(("アレルギー名"))

    class Meta:
        verbose_name = ("allergies")
        verbose_name_plural = ("allergies")

    def __str__(self):
        return self.allergy_name


class Genres(models.Model):
    genre_name = models.TextField(('ジャンル名'))

    class Meta:
        verbose_name = ("Genres")
        verbose_name_plural = ("Genres")

    def __str__(self):
        return self.genre_name


class Menu(models.Model):
    menu_name = models.CharField(("名前"), max_length=128, unique=True)
    menu_value = models.IntegerField(("価格"))
    menu_energy = models.FloatField(("カロリー"))
    menu_carbohydrate = models.FloatField(("炭水化物"))
    menu_salt_content = models.FloatField(("塩分"))
    menu_lipid = models.FloatField(("脂質"))
    menu_protein = models.FloatField(("タンパク質"))
    menu_red_point = models.FloatField(("赤"))
    menu_green_point = models.FloatField(("緑"))
    menu_yellow_point = models.FloatField(("黄"))
    menu_picture = models.ImageField(
        ("画像"), upload_to=get_file_path, height_field=None, width_field=None, max_length=None, null=True, blank=True)
    menu_genre = models.ManyToManyField(
        Genres, verbose_name=("ジャンル"), blank=True, default=get_or_create_default_genre)
    menu_allergies = models.ManyToManyField(
        Allergies, verbose_name=("アレルギー"), blank=True)

    class Meta:
        verbose_name = ("menu")
        verbose_name_plural = ("menus")

    def __str__(self):
        return self.menu_name
