# Generated by Django 5.2.1 on 2025-05-27 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DraftPick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keeper', models.BooleanField(default=False)),
                ('player_id', models.IntegerField()),
                ('round_id', models.IntegerField()),
                ('round_pick_number', models.IntegerField()),
                ('fantasy_team_id', models.IntegerField()),
                ('overall_pick_number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_id', models.IntegerField()),
                ('player_name', models.CharField(max_length=50)),
                ('player_points', models.IntegerField()),
            ],
        ),
    ]
