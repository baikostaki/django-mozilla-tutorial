# Generated by Django 4.0.6 on 2022-08-12 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_book_cover_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(null=True, upload_to='book_covers/'),
        ),
    ]
