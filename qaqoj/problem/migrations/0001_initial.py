# Generated by Django 2.0.6 on 2018-07-13 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('time_limit', models.IntegerField(default=1)),
                ('memory_limit', models.IntegerField(default=256)),
                ('description', models.TextField()),
                ('input_description', models.TextField()),
                ('output_description', models.TextField()),
                ('sample_input', models.TextField()),
                ('sample_output', models.TextField()),
                ('hint', models.TextField()),
                ('ac_num', models.IntegerField(default=0)),
                ('sub_num', models.IntegerField(default=0)),
                ('visible', models.BooleanField(default=False)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('create_time',),
            },
        ),
    ]
