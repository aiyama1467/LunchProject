# Generated by Django 2.2.5 on 2019-12-15 10:54

import django.core.validators
from django.db import migrations, models
import menu_proposal.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Allergies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allergy_name', models.TextField(verbose_name='アレルギー（Allergic substance）')),
            ],
            options={
                'verbose_name': 'allergies',
                'verbose_name_plural': 'allergies',
            },
        ),
        migrations.CreateModel(
            name='Genres',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre_name', models.TextField(verbose_name='ジャンル名（Genre）')),
            ],
            options={
                'verbose_name': 'Genres',
                'verbose_name_plural': 'Genres',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu_name', models.CharField(help_text='※必須', max_length=128, unique=True, verbose_name='名前（Menu name）')),
                ('menu_value', models.IntegerField(help_text='※必須・0以上の整数', validators=[django.core.validators.MinValueValidator(0)], verbose_name='価格（Price (incl. tax)）')),
                ('menu_energy', models.FloatField(help_text='※必須・0以上の整数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='カロリー（Energy）')),
                ('menu_carbohydrate', models.FloatField(help_text='※必須・0以上の小数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='炭水化物（Carbohydrates）')),
                ('menu_salt_content', models.FloatField(help_text='※必須・0以上の小数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='塩分（Salt）')),
                ('menu_lipid', models.FloatField(help_text='※必須・0以上の小数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='脂質（Fat）')),
                ('menu_protein', models.FloatField(help_text='※必須・0以上の小数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='タンパク質（Protein）')),
                ('menu_red_point', models.FloatField(help_text='※必須・0以上の小数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='赤（Red）')),
                ('menu_green_point', models.FloatField(help_text='※必須・0以上の小数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='緑（Green）')),
                ('menu_yellow_point', models.FloatField(help_text='※必須・0以上の小数', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='黄（Yellow）')),
                ('menu_picture', models.ImageField(blank=True, help_text='※任意', null=True, upload_to=menu_proposal.models.get_file_path, verbose_name='画像（Image）')),
                ('menu_allergies', models.ManyToManyField(blank=True, help_text='※任意', null=True, to='menu_proposal.Allergies', verbose_name='アレルギー（Allergic substance）')),
                ('menu_genre', models.ManyToManyField(help_text='※1つ以上選択', to='menu_proposal.Genres', verbose_name='ジャンル（Genre）')),
            ],
            options={
                'verbose_name': 'menu',
                'verbose_name_plural': 'menus',
            },
        ),
    ]
