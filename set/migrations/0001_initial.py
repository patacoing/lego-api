# Generated by Django 4.2.16 on 2024-09-06 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('theme', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField()),
                ('num_parts', models.PositiveIntegerField()),
                ('img_url', models.URLField()),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='theme.theme')),
            ],
        ),
    ]
