# Generated by Django 2.1.7 on 2019-03-31 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_auto_20190324_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forummember',
            name='avatar',
            field=models.ImageField(default='/static/forum/entity/av_default.jpg', upload_to='static/forum/avatar'),
        ),
        migrations.AlterField(
            model_name='threadforum',
            name='category',
            field=models.PositiveIntegerField(choices=[(1, 'Accueil'), (2, 'Sonov'), (3, 'Autres sujets')]),
        ),
    ]
