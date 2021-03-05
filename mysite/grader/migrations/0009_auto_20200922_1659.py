# Generated by Django 3.0.3 on 2020-09-22 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grader', '0008_prompt'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('learner_type', models.CharField(max_length=100)),
                ('content_type', models.CharField(max_length=100)),
                ('link', models.CharField(max_length=1000)),
                ('beginner', models.BooleanField()),
                ('intermediate', models.BooleanField()),
                ('advanced', models.BooleanField()),
            ],
        ),
        migrations.AlterField(
            model_name='prompt',
            name='area',
            field=models.CharField(max_length=100),
        ),
    ]